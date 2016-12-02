#include "RooDstD0PowerBG.h"
#include "RooAbsReal.h"
#include "RooRealProxy.h"
#include "RooMath.h"

ClassImp(RooDstD0PowerBG)

RooDstD0PowerBG::RooDstD0PowerBG(const char *name, const char *title,
      RooAbsReal& _x,
      RooAbsReal& _c0,
      RooAbsReal& _c1,
      RooAbsReal& _c2,
      RooAbsReal& _c3
      ) : RooAbsPdf(name, title),
  x("x", "x", this, _x),
  c0("c0", "c0", this, _c0),
  c1("c1", "c1", this, _c1),
  c2("c2", "c2", this, _c2),
  c3("c3", "c3", this, _c3)
{
}

RooDstD0PowerBG::RooDstD0PowerBG(const RooDstD0PowerBG& pdf, const char* name) : RooAbsPdf(pdf, name),
  x("x", this, pdf.x),
  c0("c0", this, pdf.c0),
  c1("c1", this, pdf.c1),
  c2("c2", this, pdf.c2),
  c3("c3", this, pdf.c3)
{
}

Double_t RooDstD0PowerBG::evaluate() const
{
  double diff = x - c0;
  if (diff <= 0) {
      return 0;
  }
  return (c1*pow(diff, 0.5)) + (c2*pow(diff, 1.5)) + (c3*pow(diff, 2.5));
}

Int_t RooDstD0PowerBG::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const
{
  if (matchArgs(allVars, analVars, x)) {
      return 1;
  }
  return 0;
}

// Analytical integral is
//   (2/3)*c1*(x - c0)^(3/2) + (2/5)*c2*(x - c0)^(5/2) + (2/7)*c3*(x - 
//   c0)^(7/2)
Double_t RooDstD0PowerBG::analyticalIntegral(Int_t code, const char* rangeName) const
{
  assert(code == 1);

  double xmax = x.max(rangeName);
  double xmin = x.min(rangeName);
  assert(xmin < xmax);

  // Can't integrate below c0
  if (xmax <= c0) {
      return 0.0;
  }
  if (xmin <= c0) {
      xmin = c0;
  }

  double xmaxdiff = xmax - c0;
  double xmindiff = xmin - c0;

  // First compute the integral for xmax
  double intmax = (
    (2.0/3.0)*c1*pow(xmaxdiff, 1.5) +
    (2.0/5.0)*c2*pow(xmaxdiff, 2.5) +
    (2.0/7.0)*c3*pow(xmaxdiff, 3.5)
  );
  // Then compute the integral for xmin
  double intmin = (
    (2.0/3.0)*c1*pow(xmindiff, 1.5) +
    (2.0/5.0)*c2*pow(xmindiff, 2.5) +
    (2.0/7.0)*c3*pow(xmindiff, 3.5)
  );

  // Total integral is the difference between the evaluation at max and min
  return intmax - intmin;
}
