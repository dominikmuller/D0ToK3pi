#ifndef ROO_ASYM_GAUSS_EXP
#define ROO_ASYM_GAUSS_EXP

#include "RooAbsPdf.h"
#include "RooRealProxy.h"

class RooAbsReal;

class RooAsymGaussExp : public RooAbsPdf {
public:
  RooAsymGaussExp() {}
  RooAsymGaussExp(const char *name, const char *title,
    RooAbsReal& _x,
    RooAbsReal& _mean,
    RooAbsReal& _sigma,
    RooAbsReal& _asym,
    RooAbsReal& _rhoL,
    RooAbsReal& _rhoR
  );
  RooAsymGaussExp(const RooAsymGaussExp& other, const char* name = 0);
  virtual TObject* clone(const char* newname) const { return new RooAsymGaussExp(*this, newname); }
  inline virtual ~RooAsymGaussExp() {}

protected:
  RooRealProxy x;
  RooRealProxy mean;
  RooRealProxy sigma;
  RooRealProxy asym;
  RooRealProxy rhoL;
  RooRealProxy rhoR;

  Double_t evaluate() const;
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName = 0) const;
  Double_t analyticalIntegral(Int_t code, const char* rangeName = 0) const;

private:
  ClassDef(RooAsymGaussExp, 1) // Asymmetrical Gaussian with exponential tails
};

#endif
