# Fixed local ladder-Tseitin proof schemas. All 2^15 Boolean assignments
# are checked for the five-edge induction schema, then both endpoints on
# 2^9 assignments. No graph-size sweep: the notebook gives the all-r proof.
tlDomain:=function(bits,n)
  return ForAll([1..n],j->Sum(bits{[3*j-2..3*j]})=1);
end;;
tlValues:=function(bits,n)
  return List([1..n],j->Position(bits{[3*j-2..3*j]},1)-1);
end;;
tlClauses:=function(edges,signs,charge)
  local rows,vals,cl,j;
  rows:=[];
  for vals in Tuples([0,1,2],Length(edges)) do
    if Sum([1..Length(edges)],j->signs[j]*vals[j]) mod 3 <>charge then
      cl:=List([1..Length(edges)],j->3*(edges[j]-1)+vals[j]+1);
      Add(rows,cl);
    fi;
  od;
  return rows;
end;;
tlSat:=function(bits,clauses)
  return ForAll(clauses,cl->ForAny(cl,j->bits[j]=0));
end;;
# Edges: a_previous,b_previous,a_next,b_next,x.
tlMiddle:=Concatenation(tlClauses([3,1,5],[1,-1,1],0),
                        tlClauses([4,2,5],[1,-1,-1],0));;
tlPrevious:=tlClauses([1,2],[1,1],0);;
tlNext:=tlClauses([3,4],[1,1],0);;
tlLegal:=0;;tlPrem:=0;;tlWithout:=0;;tlBad:=0;;
Print("Planned Boolean cases: middle32768, endpoints512each.\n");
for tlBits in Tuples([0,1],15) do
  if tlDomain(tlBits,5) then
    tlLegal:=tlLegal+1;
    tlVal:=tlValues(tlBits,5);
    Assert(0,tlSat(tlBits,tlMiddle)=((tlVal[3]-tlVal[1]+tlVal[5]) mod 3=0 and (tlVal[4]-tlVal[2]-tlVal[5]) mod 3=0));
    if tlSat(tlBits,tlMiddle) then
      tlWithout:=tlWithout+1;
      if tlSat(tlBits,tlPrevious) then
        tlPrem:=tlPrem+1;Assert(0,tlSat(tlBits,tlNext));
        Print("middle premise ",tlVal,"\n");
      elif not tlSat(tlBits,tlNext) then
        tlBad:=tlBad+1;Print("dropped equality failure ",tlVal,"\n");
      fi;
    fi;
  fi;
od;
Assert(0,tlLegal=243 and tlPrem=9 and tlWithout=27 and tlBad=18);
# Endpoint edge list a,b,x; absent exterior rails are literal zero constants.
tlRoot:=Concatenation(tlClauses([1,3],[1,1],0),tlClauses([2,3],[1,-1],0));;
tlEnd:=Concatenation(tlClauses([1,3],[-1,1],0),tlClauses([2,3],[-1,-1],1));;
tlEqual:=tlClauses([1,2],[1,1],0);;
tlRootCount:=0;;tlEndCount:=0;;tlEndBad:=0;;
for tlBits in Tuples([0,1],9) do
  if tlDomain(tlBits,3) then
    if tlSat(tlBits,tlRoot) then
      tlRootCount:=tlRootCount+1;Assert(0,tlSat(tlBits,tlEqual));
      Print("root premise ",tlValues(tlBits,3),"\n");
    fi;
    if tlSat(tlBits,tlEnd) then
      tlEndBad:=tlEndBad+1;
      if tlSat(tlBits,tlEqual) then tlEndCount:=tlEndCount+1;fi;
      Print("end without equality ",tlValues(tlBits,3),"\n");
    fi;
  fi;
od;
Assert(0,tlRootCount=3 and tlEndCount=0 and tlEndBad=3);
Print("PASS: 33792 Boolean assignments; legal middle243, middle premises9, dropped-equality failures18; root3, end0, end without equality3.\n");
QUIT;
