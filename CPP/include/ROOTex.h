#ifndef WidthSampleBox_h
#define WidthSampleBox_h

#include "TObject.h"
#include "TMath.h"

#include <vector>
#include <cstdarg>
#include <algorithm>
#include <iostream>

class ROOTex {
  public:
  // static Double_t Leading(Double_t _one,Double_t _two){return TMath::Max(_one,_two);}
  static Double_t Leading(Double_t _one, Double_t _two, Double_t _three, Double_t _fourth) { return GetPlaced(3, 4, _one, _two, _three, _fourth); }
  static Double_t SecondLeading(Double_t _one, Double_t _two, Double_t _three, Double_t _fourth) {
    return GetPlaced(2, 4, _one, _two, _three, _fourth);
  }
  static Double_t ThirdLeading(Double_t _one, Double_t _two, Double_t _three, Double_t _fourth) {
    return GetPlaced(1, 4, _one, _two, _three, _fourth);
  }
  static Double_t FourthLeading(Double_t _one, Double_t _two, Double_t _three, Double_t _fourth) {
    return GetPlaced(0, 4, _one, _two, _three, _fourth);
  }

  static Double_t Leading(Double_t _one, Double_t _two, Double_t _three) { return GetPlaced(2, 3, _one, _two, _three); }
  static Double_t SecondLeading(Double_t _one, Double_t _two, Double_t _three) { return GetPlaced(1, 3, _one, _two, _three); }
  static Double_t ThirdLeading(Double_t _one, Double_t _two, Double_t _three) { return GetPlaced(0, 3, _one, _two, _three); }

  static Double_t Leading(Double_t _one, Double_t _two) { return GetPlaced(1, 2, _one, _two); }
  static Double_t SecondLeading(Double_t _one, Double_t _two) { return GetPlaced(0, 2, _one, _two); }

  private:
  ROOTex(){};
  virtual ~ROOTex() {}
  static Double_t GetPlaced(int i, int n, ...) {
    va_list args;
    va_start(args, n);

    std::vector<Double_t> values;
    for (int j = 0; j < n; ++j) {
      values.push_back(va_arg(args, Double_t));
    }
    va_end(args);

    std::sort(values.begin(), values.end());

    return values.at(i);
  }
  ClassDef(ROOTex, 0)
};

#endif
