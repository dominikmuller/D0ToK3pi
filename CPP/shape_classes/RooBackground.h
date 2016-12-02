#ifndef ROOBACKGROUND
#define ROOBACKGROUND

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
#include "RooTrace.h"

#include <vector>
 
class RooBackground : public RooAbsPdf {
public:
  RooBackground() { }
  RooBackground(const char *name, const char *title, RooAbsReal& _x, RooAbsReal& _par);
  RooBackground(const RooBackground& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new RooBackground(*this,newname); }
  inline virtual ~RooBackground() {  }

  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const ;
  Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const ;

  Double_t getLogVal(const RooArgSet* set=0) const ;

protected:

  RooRealProxy x ;
  RooRealProxy par;
  
  Double_t evaluate() const ;
  

private:
  ClassDef(RooBackground,3) // A Poisson PDF
};
 
#endif
