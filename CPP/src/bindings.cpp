#include "k3pi_cpp.h"

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_PLUGIN(k3pi_cpp) {
  py::module m("k3pi_cpp",
               "Because pybind11 looks more interesting than actual work.");

  m.def("treesplitter", &TreeSplitter,
        "Splits given root files and only keeps selected and specified "
        "branches. Can also add additional variables.",
        py::arg("files"), py::arg("variables"), py::arg("output"),
        py::arg("treename"), py::arg("outputtreename") = "",
        py::arg("selection") = "1",
        py::arg("addvariables") = std::map<std::string, std::string>());
  m.def("compute_delta_m", py::vectorize(compute_delta_m),
        "Computes the delta mass.",
        py::arg("extra_pt"), py::arg("extra_eta"), py::arg("extra_phi"),
        py::arg("extra_m"), py::arg("d_pt"), py::arg("d_eta"), py::arg("d_phi"),
        py::arg("d_m"));
  m.def("compute_dstp_pt", py::vectorize(compute_dstp_pt),
        "Computes the delta mass.",
        py::arg("extra_pt"), py::arg("extra_eta"), py::arg("extra_phi"),
        py::arg("extra_m"), py::arg("d_pt"), py::arg("d_eta"), py::arg("d_phi"),
        py::arg("d_m"));
  m.def("compute_delta_angle", py::vectorize(compute_delta_angle),
        "Computes the delta mass.",
        py::arg("extra_pt"), py::arg("extra_eta"), py::arg("extra_phi"),
        py::arg("extra_m"), py::arg("d_pt"), py::arg("d_eta"), py::arg("d_phi"),
        py::arg("d_m"));

  return m.ptr();
}
