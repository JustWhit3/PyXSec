#!/bin/bash

# ---------------------- Metadata ----------------------
#
# File name:  whole_comparison.sh
# Author:     Gianluca Bianco (biancogianluca9@gmail.com)
# Date:       2023-06-28
# Copyright:  (c) 2023 Gianluca Bianco under the MIT license.

# Input variables
prediction="data/nominal/input/mc.TotalPrediction_DR_dyn.nominal.observables_final.v34_2.root"
signal_theory="data/nominal/input/mc.TotalSignal_DR_dyn.nominal.observables_final.v34_2.root"
signal="data/nominal/input/mc.TotalSignal_DR_dyn.nominal.observables_final.v34_2.root"
background="data/nominal/input/mc.AllBkg.nominal.observables_final.v34_2.root"
selection_reco="2j2b70_emu"
selection_particle="2j2b_emu"
variables="m_l1l2 pT_lep1 pT_lep2 pT_jet1 pT_jet2 m_bbll mT_ttbar pT_b1b2 pT_ttbar pT_bbll"
toys="0"
data_dir="data/nominal/output"
systematic="nominal"
covariance="no"

for var in ${variables}
do
    dir="${data_dir}/${var}"
    mkdir -p "${dir}"

    # Generate theory config file
    rm -f ${dir}/config_theory.xml
    cp data/template_RooUnfold.xml ${dir}
    mv ${dir}/template_RooUnfold.xml ${dir}/config_theory.xml 
    sed -i "s#@PREDICTION@#$prediction#g" ${dir}/config_theory.xml 
    sed -i "s#@SIGNAL@#$signal_theory#g" ${dir}/config_theory.xml 
    sed -i "s#@BACKGROUND@#$background#g" ${dir}/config_theory.xml 
    sed -i "s#@RECO@#$selection_reco#g" ${dir}/config_theory.xml 
    sed -i "s#@PARTICLE@#$selection_particle#g" ${dir}/config_theory.xml 
    sed -i "s#@VARIABLE@#$var#g" ${dir}/config_theory.xml 
    sed -i "s#@TOYS@#$toys#g" ${dir}/config_theory.xml 

    # Create theory file
    echo ""
    python src/PyXSec/PyXSec.py \
        --config=${dir}/config_theory.xml  \
        --systematic=${systematic} \
        --output="${dir}/output_theory.root"

    # Generate RooUnfold config file
    rm -f ${dir}/config_RooUnfold.xml
    cp data/template_RooUnfold.xml ${dir}
    mv ${dir}/template_RooUnfold.xml ${dir}/config_RooUnfold.xml 
    sed -i "s#@PREDICTION@#$prediction#g" ${dir}/config_RooUnfold.xml 
    sed -i "s#@SIGNAL@#$signal#g" ${dir}/config_RooUnfold.xml 
    sed -i "s#@BACKGROUND@#$background#g" ${dir}/config_RooUnfold.xml 
    sed -i "s#@RECO@#$selection_reco#g" ${dir}/config_RooUnfold.xml 
    sed -i "s#@PARTICLE@#$selection_particle#g" ${dir}/config_RooUnfold.xml 
    sed -i "s#@VARIABLE@#$var#g" ${dir}/config_RooUnfold.xml 
    sed -i "s#@TOYS@#$toys#g" ${dir}/config_RooUnfold.xml 

    # Create RooUnfold file
    echo ""
    python src/PyXSec/PyXSec.py \
        --config=${dir}/config_RooUnfold.xml  \
        --systematic=${systematic} \
        --output="${dir}/output_RooUnfold.root"

    # Generate QUnfold config file
    rm -f ${dir}/config_QUnfold.xml
    cp data/template_QUnfold.xml ${dir}
    mv ${dir}/template_QUnfold.xml ${dir}/config_QUnfold.xml 
    sed -i "s#@PREDICTION@#$prediction#g" ${dir}/config_QUnfold.xml 
    sed -i "s#@SIGNAL@#$signal#g" ${dir}/config_QUnfold.xml 
    sed -i "s#@BACKGROUND@#$background#g" ${dir}/config_QUnfold.xml 
    sed -i "s#@RECO@#$selection_reco#g" ${dir}/config_QUnfold.xml 
    sed -i "s#@PARTICLE@#$selection_particle#g" ${dir}/config_QUnfold.xml 
    sed -i "s#@VARIABLE@#$var#g" ${dir}/config_QUnfold.xml 
    sed -i "s#@TOYS@#$toys#g" ${dir}/config_QUnfold.xml 

    # Create QUnfold file
    echo ""
    python src/PyXSec/PyXSec.py \
        --config=${dir}/config_QUnfold.xml  \
        --systematic=${systematic} \
        --output="${dir}/output_QUnfold.root"

    # Make comparison plots
    echo ""
    python studies/comparisons.py \
        --qunfold="${dir}/output_QUnfold.root" \
        --roounfold="${dir}/output_RooUnfold.root" \
        --theory="${dir}/output_theory.root" \
        --covariance="${covariance}"
    mv "studies/img/comparisons/AbsoluteDiffXs.png" "studies/img/comparisons/${var}_AbsoluteDiffXs.png"
done