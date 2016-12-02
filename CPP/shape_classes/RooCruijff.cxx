#include "RooCruijff.h"
#include "RooAbsReal.h"
#include "RooMath.h"
#include "RooRealProxy.h"

ClassImp(RooCruijff)

    RooCruijff::RooCruijff(const char* name, const char* title, RooAbsReal& _x,
                           RooAbsReal& _mean, RooAbsReal& _sigmaL,
                           RooAbsReal& _sigmaR, RooAbsReal& _alphaL,
                           RooAbsReal& _alphaR)
    : RooAbsPdf(name, title),
      x("x", "x", this, _x),
      mean("mean", "mean", this, _mean),
      sigmaL("sigmaL", "sigmaL", this, _sigmaL),
      sigmaR("sigmaR", "sigmaR", this, _sigmaR),
      alphaL("alphaL", "alphaL", this, _alphaL),
      alphaR("alphaR", "alphaR", this, _alphaR) {}

RooCruijff::RooCruijff(const RooCruijff& pdf, const char* name)
    : RooAbsPdf(pdf, name),
      x("x", this, pdf.x),
      mean("mean", this, pdf.mean),
      sigmaL("sigmaL", this, pdf.sigmaL),
      sigmaR("sigmaR", this, pdf.sigmaR),
      alphaL("alphaL", this, pdf.alphaL),
      alphaR("alphaR", this, pdf.alphaR)

{}

Double_t RooCruijff::evaluate() const {
  double dm2 = (x - mean) * (x - mean);
  double denom = 0.;
  if (x < mean) {
    denom = 2 * sigmaL * sigmaL + alphaL * dm2;
    return exp(-dm2 / denom);
  } else {
    denom = 2 * sigmaR * sigmaR + alphaR * dm2;
  }
  return exp(-dm2 / denom);
}

Int_t RooCruijff::getAnalyticalIntegral(RooArgSet& , RooArgSet& ,
                                        const char* ) const {
  return 0;
}

// Analytical integral is
//   (2/3)*c1*(x - c0)^(3/2) + (2/5)*c2*(x - c0)^(5/2) + (2/7)*c3*(x -
//   c0)^(7/2)
Double_t RooCruijff::analyticalIntegral(Int_t ,
                                        const char* ) const {
  assert(1);
  // Total integral is the difference between the evaluation at max and min
  return 1.;
}
