import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/hooks'))
import codex_stop_checks as hook
import stop_checks
sys.path.insert(0,str(ROOT/'tools/tests'))
from test_stop_checks import MACHINERY, needs_machinery, tasks_with_a_request


class NativeClaimTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'rollout.jsonl'
        # The gate reads the fixture's task records, not this clone's.
        self.root=Path(self.tmp.name)/'clone';(self.root/stop_checks.PROTOCOL).parent.mkdir(parents=True)
        if MACHINERY:(self.root/stop_checks.PROTOCOL).write_text('# protocol\n')
        # The checks this branch turns off are the fixture's too, not this clone's.
        own=patch.object(hook,'ROOT',self.root);own.start();self.addCleanup(own.stop)
        gate=patch.object(hook,'waiting_block',lambda root:stop_checks.waiting_block(self.root))
        gate.start();self.addCleanup(gate.stop)
        self.prompt={'type':'event_msg','payload':{'type':'user_message','message':'request'}}
        self.write(self.prompt)
        self.reply='Git has no way to show a staged file.'
        self.event={'last_assistant_message':self.reply,'transcript_path':str(self.path)}
        self.raw={'kind':'missing-feature','quote':self.reply,'tool':'Git','checked':False,'declared':False,'reason':'Check Git help.'}

    def write(self,*events):self.path.write_text(''.join(json.dumps(x)+'\n' for x in events))

    def item(self,value):return {'type':'event_msg','payload':{'type':'item_completed','item':value}}

    def result(self,raw=None):return subprocess.CompletedProcess([],0,json.dumps({'result':self.raw if raw is None else raw}), '')

    def test_readonly_mcp_fixture_protocol(self):
        messages=[{'id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18'}},
                  {'method':'notifications/initialized'}, {'id':2,'method':'tools/list'},
                  {'id':3,'method':'tools/call','params':{'name':'lookup_capability'}}]
        run=subprocess.run([sys.executable,str(ROOT/'tools/tests/fixtures/mcp_readonly.py')],
            input=''.join(json.dumps(x)+'\n' for x in messages),capture_output=True,text=True,timeout=2)
        self.assertEqual(run.returncode,0,run.stderr)
        responses=[json.loads(x) for x in run.stdout.splitlines()]
        self.assertEqual([x['id'] for x in responses],[1,2,3])
        self.assertTrue(responses[1]['result']['tools'][0]['annotations']['readOnlyHint'])
        self.assertIn('available',responses[2]['result']['content'][0]['text'])

    def test_block_exact_quote_one_continuation_and_checked_pass(self):
        with patch.object(hook.subprocess,'run',return_value=self.result()) as run:
            decision=hook.check(self.event)
            self.assertEqual(decision['decision'],'block')
            self.assertIn(self.reply,decision['reason'])
            self.assertIn('Check',decision['reason'])
            self.assertEqual(run.call_args.kwargs['timeout'],6.5)
            self.assertEqual(stop_checks.JUDGE_TIMEOUT,9.5)
            from codex_judge import INFERENCE_SECONDS
            self.assertEqual(INFERENCE_SECONDS,6.0)
            registration=json.loads((ROOT/'.codex/hooks.json').read_text())['hooks']
            self.assertEqual(registration['Stop'][0]['hooks'][0]['timeout'],7)
            request=json.loads(run.call_args.kwargs['input'])
            self.assertEqual(request['schema'],hook.SCHEMA)
            self.assertIn('at most eight words',request['prompt'])
            self.assertIn(self.reply,request['prompt'])
            self.assertIn('(none)',request['prompt'])
            self.assertNotIn('$REPLY',request['prompt'])
            self.assertNotIn('$TOOL_CALLS',request['prompt'])
            self.assertEqual(run.call_args.args[0],[sys.executable,str(hook.ROOT/'tools/codex_judge.py')])
            self.assertTrue(run.call_args.kwargs['capture_output'])
            self.assertTrue(run.call_args.kwargs['text'])
            run.reset_mock()
            self.assertEqual(hook.check({**self.event,'stop_hook_active':True}),{})
            run.assert_not_called()
        for change in ({'checked':True},{'declared':True},{'kind':'other'},{'quote':'invented sentence'}):
            with patch.object(hook.subprocess,'run',return_value=self.result({**self.raw,**change})):
                self.assertEqual(hook.check(self.event),{})

    @needs_machinery
    def test_blocks_while_a_request_waits_for_the_judge_before_the_judge_runs(self):
        tasks_with_a_request(self.root,judged=False)
        with patch.object(hook.subprocess,'run',return_value=self.result()) as run:
            decision=hook.check({**self.event,'last_assistant_message':None})
            self.assertEqual(hook.check({**self.event,'stop_hook_active':True}),{})
        run.assert_not_called()
        self.assertEqual(decision['decision'],'block')
        self.assertIn('Requests for others wait for the judge: alpha request 1.',decision['reason'])

    @needs_machinery
    def test_without_the_task_protocol_a_waiting_request_blocks_nothing(self):
        tasks_with_a_request(self.root,judged=False)
        (self.root/stop_checks.PROTOCOL).unlink()
        with patch.dict(sys.modules,{'task_index':None}),patch.object(hook.subprocess,'run',return_value=self.result(dict(self.raw,kind='other'))):
            self.assertEqual(hook.check(self.event),{})
            self.assertEqual(hook.check({**self.event,'last_assistant_message':'From now on I will fetch first.'})['decision'],'block')

    def test_a_check_the_branch_turns_off_does_not_run(self):
        gap,promise='Its plugins are unchecked.','From now on I will fetch first.'
        (self.root/'tools/hooks').mkdir(parents=True)
        with patch.object(hook,'ROOT',self.root),patch.object(hook.subprocess,'run',return_value=self.result(dict(self.raw,quote=gap))) as run:
            self.assertIn('A declared gap',hook.check({**self.event,'last_assistant_message':gap})['reason'])
            (self.root/stop_checks.CHECKS_OFF).write_text('gap\n')
            self.assertIn('promise',hook.check({**self.event,'last_assistant_message':gap+' '+promise})['reason'].lower())
            run.assert_not_called()
            self.assertIn('Unchecked claim',hook.check({**self.event,'last_assistant_message':gap})['reason'])
            self.assertEqual(run.call_count,1)
            (self.root/stop_checks.CHECKS_OFF).write_text('gap\njudge\n')
            self.assertEqual(hook.check({**self.event,'last_assistant_message':gap}),{})
            self.assertEqual(run.call_count,1)

    def test_a_promise_in_the_final_reply_blocks_before_the_judge_runs(self):
        with patch.object(hook.subprocess,'run',return_value=self.result()) as run:
            decision=hook.check({**self.event,'last_assistant_message':'From now on I will fetch first.'})
        run.assert_not_called()
        self.assertEqual(decision['decision'],'block')
        self.assertIn('"From now on I will fetch first"',decision['reason'])

    def test_a_promise_made_mid_turn_blocks_from_the_turn_s_messages_and_reasoning_summaries(self):
        message=lambda text:self.item({'type':'AgentMessage','id':'m','content':[{'type':'Text','text':text}],'phase':'commentary'})
        reasoning=lambda *summary:self.item({'type':'Reasoning','id':'r','summary_text':list(summary),'raw_content':[]})
        earlier=[message('Next time I will run it first.'),self.prompt]
        quiet=[message('Reading the file.'),reasoning(),self.item({'type':'FileChange'}),message('')]
        for name,events,found in (('a message',quiet+[message('From now on I will fetch first.')],'"From now on I will fetch first"'),
                                  ('a reasoning summary',[reasoning('Plan.','I should have timed it before the commit.')]+quiet,
                                   '"I should have timed it before the commit"'),
                                  ('the turn before',quiet,None),('no rollout',None,None)):
            with self.subTest(name=name),patch.object(hook.subprocess,'run',return_value=self.result({**self.raw,'kind':'other'})):
                self.write(*earlier,*(events or []))
                decision=hook.check({**self.event,'last_assistant_message':'Done.',
                                     'transcript_path':str(self.path) if events is not None else str(self.path)+'.absent'})
                if found:
                    self.assertEqual(decision['decision'],'block')
                    self.assertIn('A promise about future behaviour, or an admission that implies one: '+found,decision['reason'])
                else:
                    self.assertNotIn('decision',decision)
        self.write(*earlier,message('one'),{'type':'response_item','payload':{'type':'message','role':'user'}},
                   reasoning('two','three'),b'not json'.decode(),message(' \n'),reasoning(),message('four'))
        self.assertEqual(hook.said(self.path),['two\nthree','four'])
        self.write(self.item({'type':'AgentMessage','content':'not a list'}),message('five'),self.item({'type':'UserMessage'}),message('six'))
        self.assertEqual(hook.said(self.path),['six'])
        self.assertEqual(hook.said(None),[])

    def test_a_gap_declared_in_the_final_reply_asks_for_its_routes(self):
        with patch.object(hook.subprocess,'run',return_value=self.result()) as run:
            decision=hook.check({**self.event,'last_assistant_message':'Its plugins are unchecked.'})
        run.assert_not_called()
        self.assertIn('A declared gap: "Its plugins are unchecked"',decision['reason'])

    def test_invalid_native_verdict_and_failures_are_visible(self):
        for change in ({'checked':'false'},{'quote':4},{'kind':'unknown'}):
            with patch.object(hook.subprocess,'run',return_value=self.result({**self.raw,**change})):
                self.assertIn('degraded coverage',hook.check(self.event)['systemMessage'])
        for value in ('broken',json.dumps({'error':'TimeoutError'}),json.dumps({'warning':'cleanup'})):
            with patch.object(hook.subprocess,'run',return_value=subprocess.CompletedProcess([],0,value,'')):
                self.assertIn('systemMessage',hook.check(self.event))
        with patch.object(hook.subprocess,'run',side_effect=subprocess.TimeoutExpired('judge',6.5)):
            self.assertIn('systemMessage',hook.check(self.event))
        with patch.object(hook.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','token=private')):
            result = str(hook.check(self.event))
            self.assertNotIn('token=private',result)
            self.assertIn('exit=1',result)

    def test_code_mode_completed_calls_hosted_lookup_and_privacy(self):
        secret='sk-DO_NOT_FORWARD_SECRET'
        self.write(self.prompt,
            {'type':'response_item','payload':{'type':'custom_tool_call','name':'exec','input':secret}},
            self.item({'type':'CommandExecution','command':['bash','-lc','python3 -c "'+secret+'"'],'stdout':secret,'parsed_cmd':[]}),
            self.item({'type':'CommandExecution','command':['cat','tools/CODEX.md'],'parsed_cmd':[{'type':'read','path':'tools/CODEX.md'}]}),
            self.item({'type':'Extension','kind':'web.search','query':'ignored','action':{'type':'openPage','url':'https://user:password@example.com/docs?token='+secret}}),
            self.item({'type':'Extension','kind':'web.search','query':'Git help token='+secret,'action':{'type':'search'}}))
        calls,gap=hook.evidence(self.path)
        self.assertIsNone(gap)
        self.assertIn('shell: python3',calls[0])
        self.assertIn('read: file (path omitted)',calls[1])
        self.assertEqual(calls[2],'web open: https://example.com')
        self.assertIn('web search (query omitted)',calls[3])
        self.assertNotIn(secret,str(calls));self.assertNotIn('password',str(calls))

    def test_multiline_commands_reach_judge_without_argument_contents(self):
        for command, program in (("git commit -m 'PRIVATE --help\nsecond line'", 'git'),
                                 ('python3 -c "PRIVATE\nprint(1)"', 'python3')):
            for value in (command, ['bash', '-lc', command]):
                with self.subTest(value=value):
                    self.write(self.prompt, self.item({'type':'CommandExecution',
                                                       'command':value,'parsed_cmd':[]}))
                    self.assertEqual(hook.evidence(self.path), (['shell: '+program], None))
                    with patch.object(hook.subprocess,'run',return_value=self.result()) as run:
                        self.assertEqual(hook.check(self.event)['decision'],'block')
                    prompt=json.loads(run.call_args.kwargs['input'])['prompt']
                    self.assertNotIn('PRIVATE',prompt)
                    self.assertNotIn('help lookup',prompt)

    def test_hook_prompt_preserves_prior_tool_evidence(self):
        self.write(self.prompt,self.item({'type':'CommandExecution','command':'git --help'}),
                   self.item({'type':'HookPrompt','fragments':['PRIVATE']}))
        self.assertEqual(hook.evidence(self.path), (['shell: git help lookup'], None))
        with patch.object(hook.subprocess,'run',return_value=self.result()) as run:
            self.assertEqual(hook.check(self.event)['decision'],'block')
        self.assertNotIn('PRIVATE',run.call_args.kwargs['input'])

    def test_mcp_contract_summarizes_lookup_without_result_or_prompt(self):
        self.write(self.prompt,self.item({'type':'mcpToolCall','server':'docs','tool':'search',
            'arguments':{'query':'git staged files','prompt':'PRIVATE_BODY','token':'PRIVATE_TOKEN'},
            'result':{'content':'PRIVATE_OUTPUT'}}))
        calls,gap=hook.evidence(self.path)
        self.assertIsNone(gap);self.assertEqual(calls,['MCP: docs/search query lookup (contents omitted)'])
        self.assertNotIn('PRIVATE',str(calls))

    def test_subagent_lifecycle_preserves_evidence_and_reaches_judge(self):
        for spelling in ('SubAgentActivity', 'subAgentActivity'):
            with self.subTest(spelling=spelling):
                events=[self.item({'type':spelling,'kind':kind,'agent_path':'PRIVATE_PATH',
                                  'agent_thread_id':'PRIVATE_ID','result':'PRIVATE_RESULT'})
                        for kind in ('started','interacted','interrupted','completed')]
                self.write(self.prompt,self.item({'type':'CommandExecution','command':'git --help'}),
                           *events)
                self.assertEqual(hook.evidence(self.path),(['shell: git help lookup'],None))
                with patch.object(hook.subprocess,'run',return_value=self.result()) as run:
                    self.assertEqual(hook.check(self.event)['decision'],'block')
                self.assertNotIn('PRIVATE',run.call_args.kwargs['input'])
                self.write(self.prompt,*events)
                self.assertEqual(hook.evidence(self.path),([],None))

    def test_unknown_event_diagnostics_name_discriminators_not_payloads(self):
        for value, expected in (
                ({'type':'NewUnknownTool','kind':'new.operation'},
                 'type=NewUnknownTool; kind=new.operation'),
                ({'type':'Extension','kind':'unknown'},'type=Extension; kind=unknown'),
                ({'type':'NewUnknownTool'},'type=NewUnknownTool; kind=<missing>'),
                ({'type':'PRIVATE /path','kind':{'private':'value'}},
                 'type=<invalid>; kind=<invalid>'),
                ({'type':'X'*81,'kind':42},'type=<invalid>; kind=<invalid>'),
                ({'type':'NewUnknownTool','kind':'sk-PRIVATE'},
                 'type=NewUnknownTool; kind=[redacted]')):
            with self.subTest(value=value):
                self.write(self.prompt,self.item({**value,'arguments':'PRIVATE_ARGUMENTS',
                                                 'result':'PRIVATE_RESULT'}))
                with patch.object(hook.subprocess,'run') as run:
                    message=hook.check(self.event)['systemMessage']
                    run.assert_not_called()
                self.assertIn('Unsupported completed tool event: '+expected,message)
                self.assertNotIn('PRIVATE',message)

    def test_arbitrary_query_and_url_path_contents_never_leave_reader(self):
        private='UNRECOGNIZED_PRIVATE_SOURCE_TEXT'
        items=[{'type':'Extension','kind':'web.search','query':private,'action':{'type':'search'}},
               {'type':'Extension','kind':'web.search','action':{'type':'openPage','url':'https://docs.example/'+private}},
               {'type':'McpToolCall','server':'docs','tool':'lookup','arguments':{'query':private}},
               {'type':'CommandExecution','parsed_cmd':[{'type':'search','query':private},{'type':'read','path':private}]}]
        for item in items:self.assertNotIn(private,hook.item_description(item))

    def test_newest_turn_cap_and_missing_evidence_degrade(self):
        old=self.item({'type':'CommandExecution','command':['old-program']})
        calls=[self.item({'type':'CommandExecution','command':['tool'+str(i)]}) for i in range(85)]
        self.write(old,self.prompt,*calls)
        result,gap=hook.evidence(self.path)
        self.assertIsNone(gap);self.assertEqual(len(result),80)
        self.assertIn('tool5',result[0]);self.assertIn('tool84',result[-1])
        self.assertNotIn('old-program',str(result))
        with patch.object(hook,'MAX_TRANSCRIPT',50):self.assertIsNotNone(hook.evidence(self.path)[1])
        self.write(self.prompt,self.item({'type':'NewUnknownTool'}))
        with patch.object(hook.subprocess,'run') as run:
            self.assertIn('degraded coverage',hook.check(self.event)['systemMessage']);run.assert_not_called()
        self.path.write_text('bad JSON\n')
        self.assertIsNotNone(hook.evidence(self.path)[1])
        self.assertIn('systemMessage',hook.check({**self.event,'transcript_path':None}))

    def test_safe_command_summary_never_forwards_arbitrary_arguments(self):
        self.assertIn('help lookup',hook.shell(['bash','-lc','git --help']))
        self.assertIn('tools/test.py',hook.shell('python3 tools/test.py --password secret'))
        self.assertNotIn('secret',hook.shell('python3 tools/test.py --password secret'))
        self.assertEqual(hook.safe('Authorization: Bearer abc'),'Authorization: [redacted]')
        self.assertIn('[redacted]',hook.safe('api_key=abc'))
        self.assertLessEqual(len(hook.safe('a'*300)),200)

    def test_lookup_descriptions_reach_the_native_prompt(self):
        self.write(self.prompt,self.item({'type':'CommandExecution','command':['git','--help']}),
                   self.item({'type':'Extension','kind':'web.search','action':{'query':'git show help'}}))
        with patch.object(hook.subprocess,'run',return_value=self.result({**self.raw,'checked':True})) as run:
            self.assertEqual(hook.check(self.event),{})
        prompt=json.loads(run.call_args.kwargs['input'])['prompt']
        self.assertIn('- shell: git help lookup\n- web search (query omitted)',prompt)

    def test_alternate_boundaries_and_unknown_custom_tool(self):
        for boundary in ({'type':'event_msg','payload':{'type':'task_started'}},
                         {'type':'response_item','payload':{'type':'message','role':'user'}},
                         self.item({'type':'UserMessage'})):
            with self.subTest(boundary=boundary):
                self.write(boundary,self.item({'type':'CommandExecution','command':['git','--help']}))
                calls,gap=hook.evidence(self.path);self.assertIsNone(gap);self.assertEqual(len(calls),1)
        for name in ('exec','functions.exec','apply_patch','unknown_custom'):
            self.write(self.prompt,{'type':'response_item','payload':{'type':'custom_tool_call','name':name}})
            self.assertEqual(hook.evidence(self.path)[1] is None,name!='unknown_custom')
        self.write(self.prompt,{'type':'response_item','payload':{'type':'function_call','name':'docs.search','arguments':'PRIVATE'}})
        self.assertEqual(hook.evidence(self.path),(['tool: docs.search'],None))

    def test_empty_invalid_reply_and_error_with_result(self):
        with patch.object(hook.subprocess,'run') as run:
            self.assertEqual(hook.check({}),{})
            self.assertEqual(hook.check({'last_assistant_message':'  '}),{})
            self.assertIn('systemMessage',hook.check({'last_assistant_message':{'bad':1}}))
            run.assert_not_called()
        for details, reason in (
                ({'error':'TimeoutError'}, 'native inference failed: TimeoutError'),
                ({'warning':'Cleanup incomplete','cleanup_error':'TimeoutError'},
                 'native cleanup failed: TimeoutError'),
                ({'error':'NativeError','warning':'Cleanup incomplete','cleanup_error':'RuntimeError'},
                 'native inference failed: NativeError; native cleanup failed: RuntimeError'),
                ({'error':'NativeError','error_details':{'stage':'thread/start',
                  'message':'code=-1 token=PRIVATE','elapsed_seconds':.2,'deadline_seconds':4.2,
                  'stage_seconds':{'connect':.05,'thread/start':.15}}},
                 'native inference failed: NativeError [stage=thread/start, message=code=-1 [redacted], '
                 "elapsed_seconds=0.2, deadline_seconds=4.2, stage_seconds={'connect': 0.05, 'thread/start': 0.15}]"),
                ({'warning':'Cleanup incomplete','cleanup_error':'TimeoutError',
                  'cleanup_details':{'stage':'unsubscribe','message':'','elapsed_seconds':.1,
                                     'deadline_seconds':.1}},
                 'native cleanup failed: TimeoutError [stage=unsubscribe, elapsed_seconds=0.1, '
                 'deadline_seconds=0.1]'),
                ({'error':'PRIVATE_DIAGNOSTIC'}, 'native inference failed: unknown error type'),
                ({'warning':'PRIVATE_DIAGNOSTIC'}, 'native cleanup failed: unknown error type')):
            result=subprocess.CompletedProcess([],0,json.dumps({'result':self.raw,**details}),'')
            with patch.object(hook.subprocess,'run',return_value=result):
                self.assertEqual(hook.check(self.event),hook.degraded(reason))
        detail = 'x' * 220 + ' model not supported'
        self.assertIn('model not supported', hook.failure_details(
            {'error_details': {'message':detail}}, 'error_details'))
        self.assertLessEqual(len(hook.failure_details(
            {'error_details': {'message':'x' * 2000}}, 'error_details')), 620)
        for raw in ({},[],{**self.raw,'unexpected':1},{k:v for k,v in self.raw.items() if k!='reason'}):
            with patch.object(hook.subprocess,'run',return_value=self.result(raw)):
                self.assertIn('systemMessage',hook.check(self.event))

    def test_description_variants_and_secret_redaction(self):
        for secret in ('sk-ABC123','ghp_AbC123','gho_abc123'):
            self.assertEqual(hook.safe(secret),'[redacted]')
        for shell in ('bash','sh','zsh'):
            self.assertIn('git help lookup',hook.shell([shell,'-lc','git --help']))
        self.assertEqual(hook.shell(['python3','tools/Test.py','--flag']),'shell: python3 tools/Test.py')
        self.assertNotIn('help lookup',hook.shell('git status'))
        for command in ('man git','help git'):self.assertIn('help lookup',hook.shell(command))
        self.assertEqual(hook.shell(''),'shell: empty')
        self.assertEqual(hook.shell('API_KEY=hidden git'),'shell: shell')
        self.assertEqual(hook.item_description({'type':'CommandExecution','parsed_cmd':[{'type':'read','name':'README.md'},{'type':'search','query':'native hooks'}]}),'read: file (path omitted); search: repository text (query omitted)')
        for kind in ('Reasoning','AgentMessage','UserMessage','ContextCompaction','Plan'):
            self.assertIsNone(hook.item_description({'type':kind}))
        self.assertIn('file edit',hook.item_description({'type':'FileChange'}))
        self.assertEqual(hook.item_description({'type':'McpToolCall','server':'docs','tool':'get','arguments':{'url':'https://example.com/a?token=secret'}}),'MCP: docs/get https://example.com')
        with self.assertRaises(ValueError):hook.item_description({'type':'Extension','kind':'unknown'})


if __name__=='__main__':unittest.main()
