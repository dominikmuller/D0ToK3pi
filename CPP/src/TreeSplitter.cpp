#include "TBranch.h"
#include "TDirectory.h"
#include "TFile.h"
#include "TTree.h"
#include "TChain.h"
#include "TTreeFormula.h"

#include <string>
#include <iostream>
#include <unordered_map>
#include <map>
#include <vector>

#include "k3pi_cpp.h"

void TreeSplitter(std::vector<std::string> files,
                  std::vector<std::string> variables, std::string output,
                  std::string treename, std::string outputtreename,
                  std::string selection,
                  std::map<std::string, std::string> addvariables) {
  if (outputtreename == "") {
    outputtreename = treename;
  }
  auto inputtree = new TChain("", "");

  for (auto &name : files) {
    inputtree->AddFile(name.data(), TChain::kBigNumber, treename.data());
  }

  if (!variables.empty()) inputtree->SetBranchStatus("*", 0);

  for (auto &var : variables) {
    if (inputtree->GetListOfBranches()->FindObject(var.data()) != nullptr) {
      inputtree->SetBranchStatus(var.data(), 1);
    }
  }

  auto outputfile = new TFile(output.data(), "RECREATE");
  TDirectory *dir = nullptr;
  while (treename.find("/") != std::string::npos) {
    size_t pos = treename.find("/");
    std::string dirname = treename.substr(0, pos);
    treename = treename.substr(pos + 1, treename.length());
    dir = outputfile->mkdir(dirname.data());
    dir->cd();
  }
  auto outputtree = inputtree->CopyTree(selection.data());
  if (dir != nullptr) {
    outputtree->SetDirectory(dir);
  }

  // auto outputtree = inputtree->CloneTree(-1);
  auto nEvents = outputtree->GetEntries();

  std::unordered_map<TBranch *, std::pair<TTreeFormula *, Double_t *>> branches;
  std::vector<TBranch *> newBranches;
  std::vector<TTreeFormula *> formula;
  for (auto &new_pair : addvariables) {
    auto store = new Double_t(0);
    auto form = new TTreeFormula(new_pair.first.data(), new_pair.second.data(),
                                 outputtree);
    auto branch = outputtree->Branch(new_pair.first.data(), store);

    branches[branch] = std::make_pair(form, store);
  }
  for (auto iEvent = 0; iEvent < nEvents; ++iEvent) {
    outputtree->LoadTree(iEvent);
    for (auto &br_conf : branches) {
      *(br_conf.second.second) = br_conf.second.first->EvalInstanceLD();
      br_conf.first->Fill();
    }
  }

  if (dir != nullptr) {
    dir->WriteTObject(outputtree);
  } else {
    outputfile->WriteTObject(outputtree);
  }
  outputfile->Close();
}
