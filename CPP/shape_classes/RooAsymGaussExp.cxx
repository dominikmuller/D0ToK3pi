// Asymmetrical Gaussian with exponential tails
// parameters:
//   mean - position at maximum
//   sigma - sigma of the Gaussian
//   asym - asymmetry of the Gaussian ( sigmaLeft = sigma * (1 - asym), sigmaRight = sigma * (1 + asym) )
//   rhoL - number of sigmas from mean where left tail starts: mean - rhoL * sigmaLeft
//   rhoR - number of sigmas from mean where right tail starts: mean + rhoR * sigmaRight
//
// Allowed values of parameters: sigma > 0, -1 < asym < 1, rhoL > 0, rhoR > 0

#include "Riostream.h"

#include "RooAsymGaussExp.h"
#include "RooAbsReal.h"
#include "RooRealProxy.h"
#include "RooMath.h"

ClassImp(RooAsymGaussExp)

RooAsymGaussExp::RooAsymGaussExp(const char *name, const char *title,
      RooAbsReal& _x,
      RooAbsReal& _mean,
      RooAbsReal& _sigma,
      RooAbsReal& _asym,
      RooAbsReal& _rhoL,
      RooAbsReal& _rhoR
      ) : RooAbsPdf(name, title),
  x("x", "x", this, _x),
  mean("mean", "mean", this, _mean),
  sigma("sigma", "sigma", this, _sigma),
  asym("asym", "asym", this, _asym),
  rhoL("rhoL", "rhoL", this, _rhoL),
  rhoR("rhoR", "rhoR", this, _rhoR)
{
}

RooAsymGaussExp::RooAsymGaussExp(const RooAsymGaussExp& pdf, const char* name) : RooAbsPdf(pdf, name),
  x("x", this, pdf.x),
  mean("mean", this, pdf.mean),
  sigma("sigma", this, pdf.sigma),
  asym("asym", this, pdf.asym),
  rhoL("rhoL", this, pdf.rhoL),
  rhoR("rhoR", this, pdf.rhoR)
{
}

Double_t RooAsymGaussExp::evaluate() const
{
  assert(sigma > 0 && rhoL > 0 && rhoR > 0 && fabs(asym) < 1);

  // Shift to mean
  double x_ = x - mean;
  // Number of sigmas from center where the exponential behavior starts
  double rho;
  double sigma_;

  if(x_ > 0) {
    // Right side: use rhoR and sigma * (1 + asym)
    sigma_ = sigma * (1.0 + asym);
    rho = rhoR;
  } else {
    // Left side: use rhoL and sigma * (1 - asym)
    sigma_ = sigma * (1.0 - asym);
    rho = rhoL;
  }

  x_ = fabs(x_/sigma_);
  rho = fabs(rho);

  if(x_ < rho) {
    // Gaussian behavior
    return exp(x_ * x_ / -2.0);
  } else {
    // exponential behavior: rho * rho / 2.0 is a normalization
    return exp(rho * (rho / 2.0 - x_));
  }
}

Int_t RooAsymGaussExp::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const
{
  if(matchArgs(allVars, analVars, x)) return 1;
  return 0;
}

Double_t RooAsymGaussExp::analyticalIntegral(Int_t code, const char* rangeName) const
{
  assert(code == 1);
  assert(sigma > 0 && rhoL > 0 && rhoR > 0 && fabs(asym) < 1);

  static const double root2 = sqrt(2.0);
  static const double rootPiBy2 = sqrt(atan2(0.0, -1.0) / 2.0);

  double l = x.min(rangeName) - mean;
  double r = x.max(rangeName) - mean;
  double sl = sigma * (1.0 - asym);
  double sr = sigma * (1.0 + asym);

  if (l < 0 && r > 0) {
    double l_ = fabs(l/sl);
    double r_ = fabs(r/sr);
    double intL = 0;
    if(l_ > rhoL) {
      intL = rootPiBy2 * RooMath::erf(rhoL / root2) + exp(rhoL * rhoL / 2) * (exp(-rhoL * rhoL) - exp(-l_ * rhoL)) / rhoL;
    } else {
      intL = rootPiBy2 * RooMath::erf(l_ / root2);
    }
    double intR = 0;
    if(r_ > rhoR) {
      intR = rootPiBy2 * RooMath::erf(rhoR / root2) + exp(rhoR * rhoR / 2) * (exp(-rhoR * rhoR) - exp(-r_ * rhoR)) / rhoR;
    } else {
      intR = rootPiBy2 * RooMath::erf(r_ / root2);
    }
    return intL * sl + intR * sr;
  }

  if (l < 0) {
    double l_ = fabs(l / sl);
    double r_ = fabs(r / sr);
    if (r_ > rhoL) {
      return sl * exp(rhoL * rhoL / 2) * (exp(-r_ * rhoL) - exp(-l_ * rhoL)) / rhoL;
    }
    if (l_ < rhoL) {
      return sl * rootPiBy2 * (RooMath::erf(l_ / root2) - RooMath::erf(r_ / root2));
    }
    return sl * rootPiBy2 * (RooMath::erf(rhoL / root2) - RooMath::erf(r_ / root2)) + sl * exp(rhoL * rhoL / 2) * (exp(-rhoL * rhoL) - exp(-l_ * rhoL)) / rhoL;
  }

  if (r > 0) {
    double l_ = fabs(l / sl);
    double r_ = fabs(r / sr);
    if (l_ > rhoR) {
      return sr * exp(rhoR * rhoR / 2) * (exp(-l_ * rhoR) - exp(-r_ * rhoR)) / rhoR;
    }
    if (r_ < rhoR) {
      return sr * rootPiBy2 * (RooMath::erf(r_ / root2) - RooMath::erf(l_ / root2));
    }
    return sr * rootPiBy2 * (RooMath::erf(rhoR / root2) - RooMath::erf(l_ / root2)) + sr * exp(rhoR * rhoR / 2) * (exp(-rhoR * rhoR) - exp(-r_ * rhoR)) / rhoR;
  }

  return 0;
}
