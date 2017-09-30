#include "TLorentzVector.h"
#include "k3pi_cpp.h"

double double_misid_d0_mass(double p1_pt, double p1_eta, double p1_phi,
                            double p1_m, double p2_pt, double p2_eta,
                            double p2_phi, double p2_m, double p3_pt,
                            double p3_eta, double p3_phi, double p3_m,
                            double p4_pt, double p4_eta, double p4_phi,
                            double p4_m) {
    TLorentzVector part1, part2, part3, part4;
    part1.SetPtEtaPhiM(p1_pt, p1_eta, p1_phi, p1_m);
    part2.SetPtEtaPhiM(p2_pt, p2_eta, p2_phi, p2_m);
    part3.SetPtEtaPhiM(p3_pt, p3_eta, p3_phi, p3_m);
    part4.SetPtEtaPhiM(p4_pt, p4_eta, p4_phi, p4_m);
    return (part1 + part2 + part3 + part4).M();
}

std::vector<double> compute_four_delta_mass(
    double p1_pt, double p1_eta, double p1_phi, double p1_m, double p2_pt,
    double p2_eta, double p2_phi, double p2_m, double p3_pt, double p3_eta,
    double p3_phi, double p3_m, double p4_pt, double p4_eta, double p4_phi,
    double p4_m, double ps_pt, double ps_eta, double ps_phi, double ps_m){
    TLorentzVector part1, part2, part3, part4, parts;
    part1.SetPtEtaPhiM(p1_pt, p1_eta, p1_phi, p1_m);
    part2.SetPtEtaPhiM(p2_pt, p2_eta, p2_phi, p2_m);
    part3.SetPtEtaPhiM(p3_pt, p3_eta, p3_phi, p3_m);
    part4.SetPtEtaPhiM(p4_pt, p4_eta, p4_phi, p4_m);
    parts.SetPtEtaPhiM(ps_pt, ps_eta, ps_phi, ps_m);

    double m_four = (part1 + part2 + part3 + part4).M();
    double m_five = (part1 + part2 + part3 + part4 + parts).M();

    return {m_four, m_five-m_four};
}

double change_slowpi_d0(double p1_pt, double p1_eta, double p1_phi, double p1_m,
                        double p2_pt, double p2_eta, double p2_phi, double p2_m,
                        double p3_pt, double p3_eta, double p3_phi, double p3_m,
                        double p4_pt, double p4_eta, double p4_phi, double p4_m,
                        double ps_pt, double ps_eta, double ps_phi, double ps_m,
                        double m_compare) {
    TLorentzVector part1, part2, part3, part4, parts;
    part1.SetPtEtaPhiM(p1_pt, p1_eta, p1_phi, p1_m);
    part2.SetPtEtaPhiM(p2_pt, p2_eta, p2_phi, p2_m);
    part3.SetPtEtaPhiM(p3_pt, p3_eta, p3_phi, p3_m);
    part4.SetPtEtaPhiM(p4_pt, p4_eta, p4_phi, p4_m);
    parts.SetPtEtaPhiM(ps_pt, ps_eta, ps_phi, ps_m);
    double m_not_3 = (part1 + part2 + part4 + parts).M();
    double m_not_4 = (part1 + part2 + part3 + parts).M();
    if (fabs(m_not_3 - m_compare) < fabs(m_not_4 - m_compare)) {
        return m_not_3;
    } else {
        return m_not_4;
    }
}

double change_slowpi_d0_ws(double p1_pt, double p1_eta, double p1_phi,
                           double p1_m, double p2_pt, double p2_eta,
                           double p2_phi, double p2_m, double p3_pt,
                           double p3_eta, double p3_phi, double p3_m,
                           double p4_pt, double p4_eta, double p4_phi,
                           double p4_m, double ps_pt, double ps_eta,
                           double ps_phi, double ps_m, double m_compare) {
    TLorentzVector part1, part2, part3, part4, parts;
    part1.SetPtEtaPhiM(p1_pt, p1_eta, p1_phi, p1_m);
    part2.SetPtEtaPhiM(p2_pt, p2_eta, p2_phi, p2_m);
    part3.SetPtEtaPhiM(p3_pt, p3_eta, p3_phi, p3_m);
    part4.SetPtEtaPhiM(p4_pt, p4_eta, p4_phi, p4_m);
    parts.SetPtEtaPhiM(ps_pt, ps_eta, ps_phi, ps_m);
    double m_not_4 = (part1 + part2 + part3 + parts).M();
    return m_not_4;
}
