#include "TGenPhaseSpace.h"
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
        throw std::runtime_error("number of dimensions must be one");

    auto shape = info_ap1_pt.shape[0];
    if ((info_ap1_pt.shape[0] != shape) || (info_ap1_eta.shape[0] != shape) ||
        (info_ap1_phi.shape[0] != shape) || (info_ap2_pt.shape[0] != shape) ||
        (info_ap2_eta.shape[0] != shape) || (info_ap2_phi.shape[0] != shape) ||
        (info_ap3_pt.shape[0] != shape) || (info_ap3_eta.shape[0] != shape) ||
        (info_ap3_phi.shape[0] != shape) || (info_ap4_pt.shape[0] != shape) ||
        (info_ap4_eta.shape[0] != shape) || (info_ap4_phi.shape[0] != shape))
        throw std::runtime_error("input shapes must be equal");

    std::vector<double> m12(shape);
    std::vector<double> m34(shape);
    std::vector<double> cos1(shape);
    std::vector<double> cos2(shape);
    std::vector<double> phi1(shape);
    for (unsigned int idx = 0; idx < shape; idx++) {
        auto ret = phsp_variables(
            ((double*)info_ap1_pt.ptr)[idx], ((double*)info_ap1_eta.ptr)[idx],
            ((double*)info_ap1_phi.ptr)[idx], p1_m,
            ((double*)info_ap2_pt.ptr)[idx], ((double*)info_ap2_eta.ptr)[idx],
            ((double*)info_ap2_phi.ptr)[idx], p2_m,
            ((double*)info_ap3_pt.ptr)[idx], ((double*)info_ap3_eta.ptr)[idx],
            ((double*)info_ap3_phi.ptr)[idx], p3_m,
            ((double*)info_ap4_pt.ptr)[idx], ((double*)info_ap4_eta.ptr)[idx],
            ((double*)info_ap4_phi.ptr)[idx], p4_m);
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

std::vector<py::array_t<double>> vec_phsp_variables_maxime(
    py::array_t<double> ap1_e, py::array_t<double> ap1_px,
    py::array_t<double> ap1_py, py::array_t<double> ap1_pz, py::array_t<double> ap2_e,
    py::array_t<double> ap2_px, py::array_t<double> ap2_py, py::array_t<double> ap2_pz,
    py::array_t<double> ap3_e, py::array_t<double> ap3_px,
    py::array_t<double> ap3_py, py::array_t<double> ap3_pz, py::array_t<double> ap4_e,
    py::array_t<double> ap4_px, py::array_t<double> ap4_py, py::array_t<double> ap4_pz) {
    py::buffer_info info_ap1_e = ap1_e.request();
    py::buffer_info info_ap1_px = ap1_px.request();
    py::buffer_info info_ap1_py = ap1_py.request();
    py::buffer_info info_ap1_pz = ap1_pz.request();

    py::buffer_info info_ap2_e = ap2_e.request();
    py::buffer_info info_ap2_px = ap2_px.request();
    py::buffer_info info_ap2_py = ap2_py.request();
    py::buffer_info info_ap2_pz = ap2_pz.request();

    py::buffer_info info_ap3_e = ap3_e.request();
    py::buffer_info info_ap3_px = ap3_px.request();
    py::buffer_info info_ap3_py = ap3_py.request();
    py::buffer_info info_ap3_pz = ap3_pz.request();

    py::buffer_info info_ap4_e = ap4_e.request();
    py::buffer_info info_ap4_px = ap4_px.request();
    py::buffer_info info_ap4_py = ap4_py.request();
    py::buffer_info info_ap4_pz = ap4_pz.request();

    if ((info_ap1_e.ndim != 1) || (info_ap1_px.ndim != 1) ||
        (info_ap1_py.ndim != 1) || (info_ap1_pz.ndim != 1)||(info_ap2_e.ndim != 1) ||
        (info_ap2_px.ndim != 1) || (info_ap2_py.ndim != 1)|| (info_ap2_pz.ndim != 1) ||
        (info_ap3_e.ndim != 1) || (info_ap3_px.ndim != 1) ||
        (info_ap3_py.ndim != 1)|| (info_ap3_pz.ndim != 1) || (info_ap4_e.ndim != 1) ||
        (info_ap4_px.ndim != 1) || (info_ap4_py.ndim != 1)|| (info_ap4_pz.ndim != 1))
        throw std::runtime_error("number of dimensions must be one");

    auto shape = info_ap1_e.shape[0];
    if ((info_ap1_e.shape[0] != shape) || (info_ap1_px.shape[0] != shape) ||
        (info_ap1_py.shape[0] != shape) || (info_ap2_e.shape[0] != shape) ||
        (info_ap2_px.shape[0] != shape) || (info_ap2_py.shape[0] != shape) ||
        (info_ap3_e.shape[0] != shape) || (info_ap3_px.shape[0] != shape) ||
        (info_ap3_py.shape[0] != shape) || (info_ap4_e.shape[0] != shape) ||
        (info_ap4_px.shape[0] != shape) || (info_ap4_py.shape[0] != shape))
        throw std::runtime_error("input shapes must be equal");

    std::vector<double> m12(shape);
    std::vector<double> m34(shape);
    std::vector<double> m14(shape);
    std::vector<double> m123(shape);
    std::vector<double> m234(shape);
    for (unsigned int idx = 0; idx < shape; idx++) {
        auto ret = phsp_variables(
            ((double*)info_ap1_e.ptr)[idx], ((double*)info_ap1_px.ptr)[idx],
            ((double*)info_ap1_py.ptr)[idx], ((double*)info_ap1_pz.ptr)[idx],
            ((double*)info_ap2_e.ptr)[idx], ((double*)info_ap2_px.ptr)[idx],
            ((double*)info_ap2_py.ptr)[idx], ((double*)info_ap2_pz.ptr)[idx],
            ((double*)info_ap3_e.ptr)[idx], ((double*)info_ap3_px.ptr)[idx],
            ((double*)info_ap3_py.ptr)[idx], ((double*)info_ap3_pz.ptr)[idx],
            ((double*)info_ap4_e.ptr)[idx], ((double*)info_ap4_px.ptr)[idx],
            ((double*)info_ap4_py.ptr)[idx], ((double*)info_ap4_pz.ptr)[idx]);
        m12[idx] = ret[0];
        m34[idx] = ret[1];
        m14[idx] = ret[2];
        m123[idx] = ret[3];
        m234[idx] = ret[4];
    }

    std::vector<size_t> strides = {sizeof(double)};
    std::vector<py::array_t<double>> ret_vec(5);
    unsigned int ndim = 1;

    ret_vec[0] = py::array(py::buffer_info(m12.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, info_ap1_e.shape, strides));
    ret_vec[1] = py::array(py::buffer_info(m34.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, info_ap1_e.shape, strides));
    ret_vec[2] = py::array(py::buffer_info(m14.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, info_ap1_e.shape, strides));
    ret_vec[3] = py::array(py::buffer_info(m123.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, info_ap1_e.shape, strides));
    ret_vec[4] = py::array(py::buffer_info(m234.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, info_ap1_e.shape, strides));

    return ret_vec;
}

std::vector<py::array_t<double>> t_gen_phasespaced(size_t n) {
    std::vector<double> m12(n);
    std::vector<double> m34(n);
    std::vector<double> cos1(n);
    std::vector<double> cos2(n);
    std::vector<double> phi1(n);
    auto gen = new TGenPhaseSpace;
    double masses[4] = {0.493677, 0.13957, 0.13957, 0.13957};
    TLorentzVector mother, p1, p2, p3, p4;
    mother.SetPtEtaPhiM(20, 0, 0, 1.86484);
    gen->SetDecay(mother, 4, masses);
    for (size_t idx = 0; idx < n; idx++) {
        // Generate until hit and miss passes
        while ((((double)std::rand() / (RAND_MAX)) * 0.15) > gen->Generate()) {
        }

        auto ret = phsp_variables(
            gen->GetDecay(0)->Pt() * 1000., gen->GetDecay(0)->Eta(),
            gen->GetDecay(0)->Phi(), gen->GetDecay(0)->M() * 1000.,
            gen->GetDecay(1)->Pt() * 1000., gen->GetDecay(1)->Eta(),
            gen->GetDecay(1)->Phi(), gen->GetDecay(1)->M() * 1000.,
            gen->GetDecay(2)->Pt() * 1000., gen->GetDecay(2)->Eta(),
            gen->GetDecay(2)->Phi(), gen->GetDecay(2)->M() * 1000.,
            gen->GetDecay(3)->Pt() * 1000., gen->GetDecay(3)->Eta(),
            gen->GetDecay(3)->Phi(), gen->GetDecay(3)->M() * 1000.);
        m12[idx] = ret[0];
        m34[idx] = ret[1];
        cos1[idx] = ret[2];
        cos2[idx] = ret[3];
        phi1[idx] = ret[4];
    }

    std::vector<size_t> strides = {sizeof(double)};
    std::vector<py::array_t<double>> ret_vec(5);
    unsigned int ndim = 1;

    std::vector<size_t> shape = {n};
    ret_vec[0] = py::array(py::buffer_info(m12.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, shape, strides));
    ret_vec[1] = py::array(py::buffer_info(m34.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, shape, strides));
    ret_vec[2] = py::array(py::buffer_info(cos1.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, shape, strides));
    ret_vec[3] = py::array(py::buffer_info(cos2.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, shape, strides));
    ret_vec[4] = py::array(py::buffer_info(phi1.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, shape, strides));

    return ret_vec;
}


std::vector<py::array_t<double>> vec_compute_four_delta_mass(
    py::array_t<double> ap1_pt, py::array_t<double> ap1_eta,
    py::array_t<double> ap1_phi, double p1_m, py::array_t<double> ap2_pt,
    py::array_t<double> ap2_eta, py::array_t<double> ap2_phi, double p2_m,
    py::array_t<double> ap3_pt, py::array_t<double> ap3_eta,
    py::array_t<double> ap3_phi, double p3_m, py::array_t<double> ap4_pt,
    py::array_t<double> ap4_eta, py::array_t<double> ap4_phi, double p4_m,
    py::array_t<double> aps_pt,
    py::array_t<double> aps_eta, py::array_t<double> aps_phi, double ps_m
    ) {
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

    py::buffer_info info_aps_pt = aps_pt.request();
    py::buffer_info info_aps_eta = aps_eta.request();
    py::buffer_info info_aps_phi = aps_phi.request();
    if ((info_ap1_pt.ndim != 1) || (info_ap1_eta.ndim != 1) ||
        (info_ap1_phi.ndim != 1) || (info_ap2_pt.ndim != 1) ||
        (info_ap2_eta.ndim != 1) || (info_ap2_phi.ndim != 1) ||
        (info_ap3_pt.ndim != 1) || (info_ap3_eta.ndim != 1) ||
        (info_ap3_phi.ndim != 1) || (info_ap4_pt.ndim != 1) ||
        (info_ap4_eta.ndim != 1) || (info_ap4_phi.ndim != 1) ||
        (info_aps_pt.ndim != 1) ||
        (info_aps_eta.ndim != 1) || (info_aps_phi.ndim != 1))
        throw std::runtime_error("number of dimensions must be one");

    auto shape = info_ap1_pt.shape[0];
    if ((info_ap1_pt.shape[0] != shape) || (info_ap1_eta.shape[0] != shape) ||
        (info_ap1_phi.shape[0] != shape) || (info_ap2_pt.shape[0] != shape) ||
        (info_ap2_eta.shape[0] != shape) || (info_ap2_phi.shape[0] != shape) ||
        (info_ap3_pt.shape[0] != shape) || (info_ap3_eta.shape[0] != shape) ||
        (info_ap3_phi.shape[0] != shape) || (info_ap4_pt.shape[0] != shape) ||
        (info_ap4_eta.shape[0] != shape) || (info_ap4_phi.shape[0] != shape)|| (info_aps_pt.shape[0] != shape) ||
        (info_aps_eta.shape[0] != shape) || (info_aps_phi.shape[0] != shape))
        throw std::runtime_error("input shapes must be equal");

    std::vector<double> four(shape);
    std::vector<double> delta(shape);
    for (unsigned int idx = 0; idx < shape; idx++) {
        auto ret = compute_four_delta_mass(
            ((double*)info_ap1_pt.ptr)[idx], ((double*)info_ap1_eta.ptr)[idx],
            ((double*)info_ap1_phi.ptr)[idx], p1_m,
            ((double*)info_ap2_pt.ptr)[idx], ((double*)info_ap2_eta.ptr)[idx],
            ((double*)info_ap2_phi.ptr)[idx], p2_m,
            ((double*)info_ap3_pt.ptr)[idx], ((double*)info_ap3_eta.ptr)[idx],
            ((double*)info_ap3_phi.ptr)[idx], p3_m,
            ((double*)info_ap4_pt.ptr)[idx], ((double*)info_ap4_eta.ptr)[idx],
            ((double*)info_ap4_phi.ptr)[idx], p4_m,
            ((double*)info_aps_pt.ptr)[idx], ((double*)info_aps_eta.ptr)[idx],
            ((double*)info_aps_phi.ptr)[idx], ps_m
            );
        four[idx] = ret[0];
        delta[idx] = ret[1];
    }

    std::vector<size_t> strides = {sizeof(double)};
    std::vector<py::array_t<double>> ret_vec(2);
    unsigned int ndim = 1;

    ret_vec[0] = py::array(py::buffer_info(four.data(), sizeof(double),
                                           py::format_descriptor<double>::value,
                                           ndim, info_ap1_pt.shape, strides));
    ret_vec[1] = py::array(py::buffer_info(delta.data(), sizeof(double),
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
    m.def("vec_phsp_variables_maxime", &vec_phsp_variables_maxime, "Adding two numpy arrays");
    m.def("vec_compute_four_delta_mass", &vec_compute_four_delta_mass, "Computes mass and delta mass for the given particles. Intended for double misid studies.");
    m.def("t_gen_phasespaced", &t_gen_phasespaced,
          "Generating some phasespace stuff");
    m.def("double_misid_d0_mass", py::vectorize(double_misid_d0_mass),
          "D0 mass");
    m.def("change_slowpi_d0", py::vectorize(change_slowpi_d0), "D0 mass");
    m.def("invariant_mass_pair", py::vectorize(invariant_mass_pair), "Invariant mass of pair");
    m.def("change_slowpi_d0_ws", py::vectorize(change_slowpi_d0_ws), "D0 mass");
    m.def("phsp_variables_m12", py::vectorize(phsp_variables_m12), "D0 mass");

    return m.ptr();
}
