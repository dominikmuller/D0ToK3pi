#ifndef _Roo_LnChisq_Smeared_
#define _Roo_LnChisq_Smeared_

#include "RooAbsPdf.h"
#include "RooRealProxy.h"

class RooRealVar;

class RooLnChisqSmeared : public RooAbsPdf {
public:
  RooLnChisqSmeared() {};
  RooLnChisqSmeared(
      const char *name,
      const char *title,
      RooAbsReal& _x,
      RooAbsReal& _mean,
      RooAbsReal& _smearL,
      RooAbsReal& _smearR
  );
  RooLnChisqSmeared(const RooLnChisqSmeared& other, const char* name=0);
  virtual TObject* clone(const char* newname) const { return new RooLnChisqSmeared(*this, newname); }
  inline virtual ~RooLnChisqSmeared() { }

  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
  Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
  RooRealProxy x;
  RooRealProxy mean;
  RooRealProxy smearL;
  RooRealProxy smearR;

  Double_t evaluate() const;
  Double_t getLogVal(const RooArgSet* set=0) const;

private:
  ClassDef(RooLnChisqSmeared, 1)
};

#endif
