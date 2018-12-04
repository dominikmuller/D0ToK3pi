#include "TLorentzVector.h"
#include "k3pi_cpp.h"

double invariant_mass_pair(double p1_pt, double p1_eta, double p1_phi,
                           double p1_m, double p2_pt, double p2_eta,
                           double p2_phi, double p2_m){
    TLorentzVector part1, part2;
    part1.SetPtEtaPhiM(p1_pt, p1_eta, p1_phi, p1_m);
    part2.SetPtEtaPhiM(p2_pt, p2_eta, p2_phi, p2_m);
    double m_not_4 = (part1 + part2).M();
    return m_not_4;
}
