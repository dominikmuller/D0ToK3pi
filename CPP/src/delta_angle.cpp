#include "k3pi_cpp.h"
#include "TLorentzVector.h"

double compute_delta_angle(double extra_pt, double extra_eta, double extra_phi, double extra_m,
                       double d_pt, double d_eta, double d_phi, double d_m){
  TLorentzVector extra, d;
  extra.SetPtEtaPhiM(extra_pt, extra_eta, extra_phi, extra_m);
  d.SetPtEtaPhiM(d_pt, d_eta, d_phi, d_m);
  return d.Angle(extra.Vect());
}
