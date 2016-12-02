/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
 * Simple Poisson PDF
 * author: Kyle Cranmer <cranmer@cern.ch>
 *                                                                           *
 *****************************************************************************/

//////////////////////////////////////////////////////////////////////////////
//
// BEGIN_HTML
// Poisson pdf
// END_HTML
//

#include <iostream>

#include "RooAbsCategory.h"
#include "RooAbsReal.h"
#include "RooBackground.h"

#include "Math/ProbFuncMathCore.h"
#include "RooMath.h"
#include "RooRandom.h"
#include "TMath.h"

#include "TError.h"

using namespace std;

ClassImp(RooBackground)

    //_____________________________________________________________________________
    RooBackground::RooBackground(const char* name, const char* title,
                                 RooAbsReal& _x, RooAbsReal& _par)
    : RooAbsPdf(name, title),
      x("x", "x", this, _x),
      par("par", "par", this, _par) {
}

//_____________________________________________________________________________
RooBackground::RooBackground(const RooBackground& other, const char* name)
    : RooAbsPdf(other, name),
      x("x", this, other.x),
      par("par", this, other.par) {
}

//_____________________________________________________________________________
Double_t RooBackground::evaluate() const {
  // Implementation in terms of the TMath Poisson function
  if (x < 139.57) {
    return 0.;
  } else {
    return sqrt(x / 139.57 - 1.) * exp(par * x / 139.57);
  }
}

//_____________________________________________________________________________
Double_t RooBackground::getLogVal(const RooArgSet* s) const {
  if (x < 139.57) {
    return -100000000000000000000000000.;
  } else {
    return 0.5 * log(x / 139.57 - 1.) + par * x / 139.57;
  }
  return RooAbsPdf::getLogVal(s);
}

//_____________________________________________________________________________
Int_t RooBackground::getAnalyticalIntegral(RooArgSet&, RooArgSet&,
                                           const char* /*rangeName*/) const {
  return 0;
}

//_____________________________________________________________________________
Double_t RooBackground::analyticalIntegral(Int_t, const char*) const {
  return 1;
}
