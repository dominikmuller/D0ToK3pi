#ifndef ROO_SMEARED_LOG_CHI_SQUARED
#define ROO_SMEARED_LOG_CHI_SQUARED

#include "RooAbsPdf.h"
#include "RooRealProxy.h"

class RooAbsReal;

class RooSmearedLogChiSquared : public RooAbsPdf {
public:
  RooSmearedLogChiSquared() {}
  RooSmearedLogChiSquared(const char *name, const char *title,
    RooAbsReal& _x,
    RooAbsReal& _mu,
    RooAbsReal& _alphaL,
    RooAbsReal& _alphaR
  );
  RooSmearedLogChiSquared(const RooSmearedLogChiSquared& other, const char* name = 0);
  virtual TObject* clone(const char* newname) const { return new RooSmearedLogChiSquared(*this, newname); }
  inline virtual ~RooSmearedLogChiSquared() {}

protected:
  RooRealProxy x;
  RooRealProxy mu;
  RooRealProxy alphaL;
  RooRealProxy alphaR;

  Double_t evaluate() const;
  Double_t getLogVal(const RooArgSet* set = 0) const;
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName = 0) const;
  Double_t analyticalIntegral(Int_t code, const char* rangeName = 0) const;

private:
  ClassDef(RooSmearedLogChiSquared, 1) // Asymmetrical smeared log(chi^2) distribution
};

#endif
