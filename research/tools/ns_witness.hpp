// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Reconstruct ordinary NS witnesses and charge each generator multiple.
#pragma once
#include "ens_symbolic.hpp"
#include <string>
namespace ns_witness {
using namespace ens_symbolic;
inline int write_terms(std::ostream& out,const Ring& ring,
                       const std::vector<Polynomial>& axioms,
                       const Polynomial& target,
                       const std::map<int,Polynomial>& cofactors,
                       int budget,const std::string& label){
    Polynomial reconstructed;int used=0;
    for(const auto& [id,q]:cofactors)if(!q.empty()){
        const auto& axiom=axioms.at(id);
        used=std::max(used,degree(q)+degree(axiom));
        if(used>budget)throw std::runtime_error("NS degree budget exceeded: "+label);
        ring.accumulate(reconstructed,ring.multiply(q,axiom));
    }
    if(reconstructed!=target || used>budget)
        throw std::runtime_error("NS identity or budget mismatch: "+label);
    // Verify before serializing the suffix, so rejected evidence is not emitted.
    out<<",\"terms\":[";bool comma=false;
    for(const auto& [id,q]:cofactors)if(!q.empty()){
        if(comma)out<<',';
        comma=true;out<<"{\"axiom_id\":"<<id<<",\"cofactor\":";
        write_json(out,q);out<<'}';
    }
    out<<"],\"witness_degree\":"<<used;
    return used;
}
} // namespace ns_witness
