#ifndef ROOCRUIJFF_H
#define ROOCRUIJFF_H

#include "RooAbsPdf.h"
#include "RooRealProxy.h"

class RooAbsReal;

class RooCruijff : public RooAbsPdf {
  public:
  RooCruijff() {}
  RooCruijff(const char* name, const char* title, RooAbsReal& _x,
             RooAbsReal& _mean, RooAbsReal& _sigmaL, RooAbsReal& _sigmaR,
             RooAbsReal& _alphaL, RooAbsReal& _alphaR);
  RooCruijff(const RooCruijff& other, const char* name = 0);
  virtual TObject* clone(const char* newname) const {
    return new RooCruijff(*this, newname);
  }
  inline virtual ~RooCruijff() {}

  protected:
  RooRealProxy x;
  RooRealProxy mean;
  RooRealProxy sigmaL;
  RooRealProxy sigmaR;
  RooRealProxy alphaL;
  RooRealProxy alphaR;

  Double_t evaluate() const;
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars,
                              const char* rangeName = 0) const;
  Double_t analyticalIntegral(Int_t code, const char* rangeName = 0) const;

  private:
  ClassDef(RooCruijff, 1)  // Empirical delta mass background shape
};

#endif
