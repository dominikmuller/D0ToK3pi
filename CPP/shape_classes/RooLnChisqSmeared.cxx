#include <math.h>

#include "Riostream.h"

#include "RooLnChisqSmeared.h"
#include "RooAbsReal.h"

RooLnChisqSmeared::RooLnChisqSmeared(const char *name,
    const char *title,
    RooAbsReal& _x,
    RooAbsReal& _mean,
    RooAbsReal& _smearL,
    RooAbsReal& _smearR
  ):
  RooAbsPdf(name, title),
  x("x", "x", this, _x),
  mean("mean", "mean", this, _mean),
  smearL("smearL", "smearL", this, _smearL),
  smearR("smearR", "smearR", this, _smearR)
{
}

RooLnChisqSmeared::RooLnChisqSmeared(const RooLnChisqSmeared& other, const char* name):
  RooAbsPdf(other,name),
  x("x", this, other.x),
  mean("mean", this, other.mean),
  smearL("smearL", this, other.smearL),
  smearR("smearR", this, other.smearR)
{
}

Double_t RooLnChisqSmeared::evaluate() const
{
  if (x <= mean) {
    return exp((smearL * x) - exp(smearL * (x - mean)));
  }
  else {
    return exp((smearL * mean) + (smearR * (x - mean)) - exp(smearR * (x - mean)));
  }
}

Double_t RooLnChisqSmeared::getLogVal(const RooArgSet* set) const
{
  /* set->Print("v"); */
  /* ((RooRealVar *)x.absArg())->Print("v"); */
  /* std::cout << ((RooRealVar *)x.absArg())->getVal() << std::endl; */
  /* assert(false); */
  double logVal(0);
  if (x <= mean) {
    logVal = (smearL * x) - exp(smearL * (x - mean));
  }
  else {
    logVal = (smearL * mean) + (smearR * (x - mean)) - exp(smearR * (x - mean));
  }
  return logVal - log(analyticalIntegral(1,0));
}

Int_t RooLnChisqSmeared::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char*) const
{
  if (matchArgs(allVars, analVars, x)) {
    return 1;
  }
  return 0;
}

Double_t RooLnChisqSmeared::analyticalIntegral(Int_t code, const char* rangeName) const
{
  switch(code)
  {
    case 1:
      {
        Double_t xmax = x.max(rangeName);
        Double_t xmin = x.min(rangeName);

        const Double_t expm1 = 0.36787944117144233;
        Double_t smearLmean = smearL * mean;
        Double_t smearRmean = smearR * mean;

        Double_t result = 0.0;
        result += (1.0/smearL) * exp(smearLmean) * (exp(-exp(smearL * xmin - smearLmean)) - expm1);
        result += (1.0/smearR) * exp(smearLmean) * (expm1 - exp(-exp(smearR * xmax - smearRmean)));
        return result;
      }
  }

  assert(0);
  return 0;
}

