// Asymmetrical, smeared log(Chi^2) distribution.
// Can be defined with the following Mathematica code:
//   ln[1] = p[x_, alphaL_, alphaR_, mu_] := Piecewise[{
//             {Exp[alphaL*x - Exp[alphaL*(x - mu)]], x <= mu},
//             {Exp[alphaL*mu + alphaR*(x - mu) - Exp[alphaR*(x - mu)]], x > mu}
//           }]
// with parameters:
//   mu - Offset of distribution center from 0
//   alphaL - Asymmetry of left hand side
//   alphaR - Asymmetry of right hand side
// Analytical integral was solved with Mathematica with the above defintion:
//   ln[2] = Integrate[p[x, alphaL, alphaR, mu], x]
#include <cmath>

#include "RooSmearedLogChiSquared.h"
#include "RooAbsReal.h"
#include "RooRealProxy.h"
#include "RooMath.h"

ClassImp(RooSmearedLogChiSquared)

RooSmearedLogChiSquared::RooSmearedLogChiSquared(const char *name, const char *title,
      RooAbsReal& _x,
      RooAbsReal& _mu,
      RooAbsReal& _alphaL,
      RooAbsReal& _alphaR
      ) : RooAbsPdf(name, title),
  x("x", "x", this, _x),
  mu("mu", "mu", this, _mu),
  alphaL("alphaL", "alphaL", this, _alphaL),
  alphaR("alphaR", "alphaR", this, _alphaR)
{
}

RooSmearedLogChiSquared::RooSmearedLogChiSquared(const RooSmearedLogChiSquared& pdf, const char* name) : RooAbsPdf(pdf, name),
  x("x", this, pdf.x),
  mu("mu", this, pdf.mu),
  alphaL("alphaL", this, pdf.alphaL),
  alphaR("alphaR", this, pdf.alphaR)
{
}

Double_t RooSmearedLogChiSquared::evaluate() const
{
  Double_t alphaL_Mu = alphaL*mu;

  if (x <= mu) {
      Double_t alphaL_X = alphaL*x;
      return exp(alphaL_X - exp(alphaL_X - alphaL_Mu));
  } else {
      Double_t alphaR_XLessMu = alphaR*(x - mu);
      return exp(alphaL_Mu + alphaR_XLessMu - exp(alphaR_XLessMu));
  }
}

Double_t RooSmearedLogChiSquared::getLogVal(const RooArgSet* set) const
{
  Double_t log_val = 0.0;

  Double_t alphaL_Mu = alphaL*mu;
  if (x <= mu) {
      Double_t alphaL_X = alphaL*x;
      log_val = alphaL_X - exp(alphaL_X - alphaL_Mu);
  } else {
      Double_t alphaR_XLessMu = alphaR*(x - mu);
      log_val = alphaL_Mu + alphaR_XLessMu - exp(alphaR_XLessMu);
  }

  return log_val - log(analyticalIntegral(1,0));
}

Int_t RooSmearedLogChiSquared::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const
{
  if(matchArgs(allVars, analVars, x)) return 1;
  return 0;
}

Double_t RooSmearedLogChiSquared::analyticalIntegral(Int_t code, const char* rangeName) const
{
  assert(code == 1);

  Double_t xLo = x.min(rangeName);
  Double_t xHi = x.max(rangeName);

  Double_t integralLo = 0.0;
  Double_t integralHi = 0.0;
  // Perform the integral piecewise, first the part below mu, then above
  // If the integral range is within a piece, i.e. fully above or below mu,
  // we only need to compute the integral in that region
  Double_t invAlphaL = 1.0/alphaL;
  Double_t invAlphaR = 1.0/alphaR;
  Double_t alphaL_Mu = alphaL*mu;
  Double_t alphaR_Mu = alphaR*mu;
  if (xLo < mu) {
      // Compute the integral below mu
      Double_t integralLoLo = -invAlphaL*exp(alphaL_Mu - exp(alphaL*xLo - alphaL_Mu));
      Double_t integralLoHi = 0.0;
      if (xHi < mu) {
          integralLoHi = -invAlphaL*exp(alphaL_Mu - exp(alphaL*xHi - alphaL_Mu));
      } else {
          integralLoHi = -invAlphaL*exp(alphaL_Mu - 1.0);
      }
      integralLo = integralLoHi - integralLoLo;
  }
  if (xHi > mu) {
      // Compute the integral above mu
      Double_t integralHiLo = 0.0;
      Double_t integralHiHi = 0.0;
      if (xLo < mu) {
          integralHiLo = -invAlphaR*(exp(alphaL_Mu - 1.0));
      } else {
          integralHiLo = -invAlphaR*(exp(alphaL_Mu - exp(alphaR*xLo - alphaR_Mu)));
      }
      integralHiHi = -invAlphaR*(exp(alphaL_Mu - exp(alphaR*xHi - alphaR_Mu)));
      integralHi = integralHiHi - integralHiLo;
  }

  return integralLo + integralHi;
}
