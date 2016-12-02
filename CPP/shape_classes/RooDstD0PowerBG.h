#ifndef ROO_ASYM_GAUSS_EXP
#define ROO_ASYM_GAUSS_EXP
// Empirical power law function to describe delta mass background shape
//
//   f(x) = \sum_{i = 1} c_i*(x - c_0)^(i - (1/2))
//
// This class implements f(x) up to i = 3.
//
// Parameters:
//   c0 - Threshold
//   c1 - Coefficient of 1/2 power term
//   c2 - Coefficient of 3/2 power term
//   c3 - Coefficient of 5/2 power term

#include "RooAbsPdf.h"
#include "RooRealProxy.h"

class RooAbsReal;

class RooDstD0PowerBG : public RooAbsPdf {
public:
  RooDstD0PowerBG() {}
  RooDstD0PowerBG(const char *name, const char *title,
    RooAbsReal& _x,
    RooAbsReal& _c0,
    RooAbsReal& _c1,
    RooAbsReal& _c2,
    RooAbsReal& _c3
  );
  RooDstD0PowerBG(const RooDstD0PowerBG& other, const char* name = 0);
  virtual TObject* clone(const char* newname) const { return new RooDstD0PowerBG(*this, newname); }
  inline virtual ~RooDstD0PowerBG() {}

protected:
  RooRealProxy x;
  RooRealProxy c0;
  RooRealProxy c1;
  RooRealProxy c2;
  RooRealProxy c3;

  Double_t evaluate() const;
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName = 0) const;
  Double_t analyticalIntegral(Int_t code, const char* rangeName = 0) const;

private:
  ClassDef(RooDstD0PowerBG, 1) // Empirical delta mass background shape
};

#endif
