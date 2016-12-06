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
                       double extra_m, double d_pt, double d_eta, double d_phi,
                       double d_m);

#endif /* ifndef k3pi_cpp */
