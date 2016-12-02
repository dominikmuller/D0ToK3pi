 /***************************************************************************** 
  * Project: RooFit                                                           * 
  *                                                                           * 
  * Simple Poisson PDF
  * author: Kyle Cranmer <cranmer@cern.ch>
  *                                                                           * 
  *****************************************************************************/ 

#ifndef ROOPOISSONFIX
#define ROOPOISSONFIX

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
#include "RooTrace.h"
 
class RooPoissonFix : public RooAbsPdf {
public:
  RooPoissonFix() { _noRounding = kFALSE ;   } ;
  RooPoissonFix(const char *name, const char *title, RooAbsReal& _x, RooAbsReal& _mean, Bool_t noRounding=kFALSE);
  RooPoissonFix(const RooPoissonFix& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new RooPoissonFix(*this,newname); }
  inline virtual ~RooPoissonFix() {  }

  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const ;
  Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const ;

  Int_t getGenerator(const RooArgSet& directVars, RooArgSet &generateVars, Bool_t staticInitOK=kTRUE) const;
  void generateEvent(Int_t code);
  
  void setNoRounding(bool flag = kTRUE){_noRounding = flag;}
  void protectNegativeMean(bool flag = kTRUE){_protectNegative = flag;}

  Double_t getLogVal(const RooArgSet* set=0) const ;

protected:

  RooRealProxy x ;
  RooRealProxy mean ;
  Bool_t  _noRounding ;
  Bool_t  _protectNegative ;
  
  Double_t evaluate() const ;
  Double_t evaluate(Double_t k) const;
  

private:

  ClassDef(RooPoissonFix,3) // A Poisson PDF
};
 
#endif
