#ifndef K3PI_CPP
#define K3PI_CPP

#include <map>
#include <string>
#include <vector>

void TreeSplitter(std::vector<std::string> files,
                  std::vector<std::string> variables, std::string output,
                  std::string treename, std::string outputtreename = "",
                  std::string selection = "1",
                  std::map<std::string, std::string> addvariables =
                      std::map<std::string, std::string>());

double compute_delta_m(double extra_pt, double extra_eta, double extra_phi,
                       double extra_m, double d_pt, double d_eta, double d_phi,
                       double d_m);
double compute_dstp_pt(double extra_pt, double extra_eta, double extra_phi,
                       double extra_m, double d_pt, double d_eta, double d_phi,
                       double d_m);
double compute_delta_angle(double extra_pt, double extra_eta, double extra_phi,
                           double extra_m, double d_pt, double d_eta,
                           double d_phi, double d_m);

std::vector<double> phsp_variables(double p1_pt, double p1_eta, double p1_phi,
                                   double p1_m, double p2_pt, double p2_eta,
                                   double p2_phi, double p2_m, double p3_pt,
                                   double p3_eta, double p3_phi, double p3_m,
                                   double p4_pt, double p4_eta, double p4_phi,
                                   double p4_m);

double phsp_variables_m12(double p1_pt, double p1_eta, double p1_phi,
                          double p1_m, double p2_pt, double p2_eta,
                          double p2_phi, double p2_m, double p3_pt,
                          double p3_eta, double p3_phi, double p3_m,
                          double p4_pt, double p4_eta, double p4_phi,
                          double p4_m);

std::vector<double> phsp_variables_maxime(
    double p1_e, double p1_px, double p1_py, double p1_pz, double p2_e,
    double p2_px, double p2_py, double p2_pz, double p3_e, double p3_px,
    double p3_py, double p3_pz, double p4_e, double p4_px, double p4_py,
    double p4_pz);

double double_misid_d0_mass(double p1_pt, double p1_eta, double p1_phi,
                            double p1_m, double p2_pt, double p2_eta,
                            double p2_phi, double p2_m, double p3_pt,
                            double p3_eta, double p3_phi, double p3_m,
                            double p4_pt, double p4_eta, double p4_phi,
                            double p4_m);

std::vector<double> compute_four_delta_mass(
    double p1_pt, double p1_eta, double p1_phi, double p1_m, double p2_pt,
    double p2_eta, double p2_phi, double p2_m, double p3_pt, double p3_eta,
    double p3_phi, double p3_m, double p4_pt, double p4_eta, double p4_phi,
    double p4_m, double ps_pt, double ps_eta, double ps_phi, double ps_m);

double change_slowpi_d0(double p1_pt, double p1_eta, double p1_phi, double p1_m,
                        double p2_pt, double p2_eta, double p2_phi, double p2_m,
                        double p3_pt, double p3_eta, double p3_phi, double p3_m,
                        double p4_pt, double p4_eta, double p4_phi, double p4_m,
                        double ps_pt, double ps_eta, double ps_phi, double ps_m,
                        double m_compare);

double change_slowpi_d0_ws(double p1_pt, double p1_eta, double p1_phi,
                           double p1_m, double p2_pt, double p2_eta,
                           double p2_phi, double p2_m, double p3_pt,
                           double p3_eta, double p3_phi, double p3_m,
                           double p4_pt, double p4_eta, double p4_phi,
                           double p4_m, double ps_pt, double ps_eta,
                           double ps_phi, double ps_m, double m_compare);

double invariant_mass_pair(double p1_pt, double p1_eta, double p1_phi,
                           double p1_m, double p2_pt, double p2_eta,
                           double p2_phi, double p2_m);

#endif /* ifndef k3pi_cpp */
