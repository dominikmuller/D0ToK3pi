#include "k3pi_cpp.h"

#include <pybind11/cast.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

std::vector<py::array_t<double>> vec_phsp_variables(
    py::array_t<double> ap1_pt, py::array_t<double> ap1_eta,
    py::array_t<double> ap1_phi, double p1_m, py::array_t<double> ap2_pt,
    py::array_t<double> ap2_eta, py::array_t<double> ap2_phi, double p2_m,
    py::array_t<double> ap3_pt, py::array_t<double> ap3_eta,
    py::array_t<double> ap3_phi, double p3_m, py::array_t<double> ap4_pt,
    py::array_t<double> ap4_eta, py::array_t<double> ap4_phi, double p4_m) {
  py::buffer_info info_ap1_pt = ap1_pt.request();
  py::buffer_info info_ap1_eta = ap1_eta.request();
  py::buffer_info info_ap1_phi = ap1_phi.request();

  py::buffer_info info_ap2_pt = ap2_pt.request();
  py::buffer_info info_ap2_eta = ap2_eta.request();
  py::buffer_info info_ap2_phi = ap2_phi.request();

  py::buffer_info info_ap3_pt = ap3_pt.request();
  py::buffer_info info_ap3_eta = ap3_eta.request();
  py::buffer_info info_ap3_phi = ap3_phi.request();

  py::buffer_info info_ap4_pt = ap4_pt.request();
  py::buffer_info info_ap4_eta = ap4_eta.request();
  py::buffer_info info_ap4_phi = ap4_phi.request();
  if ((info_ap1_pt.ndim != 1) || (info_ap1_eta.ndim != 1) ||
      (info_ap1_phi.ndim != 1) || (info_ap2_pt.ndim != 1) ||
      (info_ap2_eta.ndim != 1) || (info_ap2_phi.ndim != 1) ||
      (info_ap3_pt.ndim != 1) || (info_ap3_eta.ndim != 1) ||
      (info_ap3_phi.ndim != 1) || (info_ap4_pt.ndim != 1) ||
      (info_ap4_eta.ndim != 1) || (info_ap4_phi.ndim != 1))
    throw std::runtime_error("Number of dimensions must be one");

  auto shape = info_ap1_pt.shape[0];
  if ((info_ap1_pt.shape[0] != shape) || (info_ap1_eta.shape[0] != shape) ||
      (info_ap1_phi.shape[0] != shape) || (info_ap2_pt.shape[0] != shape) ||
      (info_ap2_eta.shape[0] != shape) || (info_ap2_phi.shape[0] != shape) ||
      (info_ap3_pt.shape[0] != shape) || (info_ap3_eta.shape[0] != shape) ||
      (info_ap3_phi.shape[0] != shape) || (info_ap4_pt.shape[0] != shape) ||
      (info_ap4_eta.shape[0] != shape) || (info_ap4_phi.shape[0] != shape))
    throw std::runtime_error("Input shapes must be equal");

  std::vector<double> m12(shape);
  std::vector<double> m34(shape);
  std::vector<double> cos1(shape);
  std::vector<double> cos2(shape);
  std::vector<double> phi1(shape);
  for (unsigned int idx = 0; idx < shape; idx++) {
    auto ret = phsp_variables(
        ((double*)info_ap1_pt.ptr)[idx], ((double*)info_ap1_eta.ptr)[idx],
        ((double*)info_ap1_phi.ptr)[idx], p1_m, ((double*)info_ap2_pt.ptr)[idx],
        ((double*)info_ap2_eta.ptr)[idx], ((double*)info_ap2_phi.ptr)[idx],
        p2_m, ((double*)info_ap3_pt.ptr)[idx], ((double*)info_ap3_eta.ptr)[idx],
        ((double*)info_ap3_phi.ptr)[idx], p3_m, ((double*)info_ap4_pt.ptr)[idx],
        ((double*)info_ap4_eta.ptr)[idx], ((double*)info_ap4_phi.ptr)[idx],
        p4_m);
    m12[idx] = ret[0];
    m34[idx] = ret[1];
    cos1[idx] = ret[2];
    cos2[idx] = ret[3];
    phi1[idx] = ret[4];
  }

  std::vector<size_t> strides = {sizeof(double)};
  std::vector<py::array_t<double>> ret_vec(5);
  unsigned int ndim = 1;

  ret_vec[0] = py::array(py::buffer_info(m12.data(), sizeof(double),
                                         py::format_descriptor<double>::value,
                                         ndim, info_ap1_pt.shape, strides));
  ret_vec[1] = py::array(py::buffer_info(m34.data(), sizeof(double),
                                         py::format_descriptor<double>::value,
                                         ndim, info_ap1_pt.shape, strides));
  ret_vec[2] = py::array(py::buffer_info(cos1.data(), sizeof(double),
                                         py::format_descriptor<double>::value,
                                         ndim, info_ap1_pt.shape, strides));
  ret_vec[3] = py::array(py::buffer_info(cos2.data(), sizeof(double),
                                         py::format_descriptor<double>::value,
                                         ndim, info_ap1_pt.shape, strides));
  ret_vec[4] = py::array(py::buffer_info(phi1.data(), sizeof(double),
                                         py::format_descriptor<double>::value,
                                         ndim, info_ap1_pt.shape, strides));

  return ret_vec;
}

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
        "Computes the delta mass.", py::arg("extra_pt"), py::arg("extra_eta"),
        py::arg("extra_phi"), py::arg("extra_m"), py::arg("d_pt"),
        py::arg("d_eta"), py::arg("d_phi"), py::arg("d_m"));
  m.def("compute_dstp_pt", py::vectorize(compute_dstp_pt),
        "Computes the delta mass.", py::arg("extra_pt"), py::arg("extra_eta"),
        py::arg("extra_phi"), py::arg("extra_m"), py::arg("d_pt"),
        py::arg("d_eta"), py::arg("d_phi"), py::arg("d_m"));
  m.def("compute_delta_angle", py::vectorize(compute_delta_angle),
        "Computes the delta mass.", py::arg("extra_pt"), py::arg("extra_eta"),
        py::arg("extra_phi"), py::arg("extra_m"), py::arg("d_pt"),
        py::arg("d_eta"), py::arg("d_phi"), py::arg("d_m"));
  m.def("vec_phsp_variables", &vec_phsp_variables, "Adding two numpy arrays");

  return m.ptr();
}
