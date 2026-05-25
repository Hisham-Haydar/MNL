## uprate_fr / Uprate
- DEF: Uprating factors
- **Dataset** = training_data
- **Def_Factor** = 1
- **WarnIfNoFactor** = no

## uprate_fr / Uprate
- DEF: Uprating factors
- **dataset** = hypodata_fr
- **def_factor** = 1
- **WarnIfNoFactor** = no
- **Dataset** = *_hhot

## uprate_fr / Uprate
- DEF: Uprating factors
- **dataset** = fr_201?_b?
- **def_factor** = $f_one
- **yse** = $f_hourly_wage
- **yiy** = $f_yiy
- **ypr** = $f_rri
- **ypp** = $f_one
- **yot** = $f_one
- **ypt** = $f_hourly_wage
- **yivwg** = $f_hourly_wage_pv
- **yempv** = $f_hourly_wage_pv
- **poa00** = $f_poa
- **bed** = $f_one
- **bunct** = $f_hourly_wage_pv
- **bunmt** = $f_bunmt
- **aggvar_name** = 6 variants
- **aggvar_part** = 15 variants
- **aggvar_tolerance** = 4 variants
- **bch00** = $f_bch00
- **bchlg** = $f_bchlg
- **bchyc** = $f_bchyc
- **bched** = $f_bched
- **bchot** = $f_bchot
- **bsa00** = $f_bsa00
- **bsaot** = $f_bsa00
- **bhl** = $f_hourly_wage_pv
- **pdi00** = 2 variants
- **bsaoa** = $f_bsaoa
- **bdi** = $f_bdi
- **afc** = $f_hicp
- **kfb** = $f_hourly_wage
- **kivho** = $f_one
- **tpr** = $f_tpr
- **tis** = $f_one
- **bsuwd** = $f_bsuwd
- **psu** = 2 variants
- **tad** = $f_one
- **xhcmomi** = $f_hicp
- **xhcrt** = $f_rri
- **xhcot** = $f_hicp
- **xmp** = $f_hicp
- **xpp** = $f_one
- **yds** = $f_one
- **bhotn** = $f_bho
- **bhoot** = $f_bho
- **WarnIfNoFactor** = yes
- **ydses_o** = $f_yds
- **kfbcc** = $f_hicp
- **tmu** = $f_tmu
- **twl** = $f_twl
- **bchcc** = $f_bchot
- **AggVar_Part** = 6 variants
- **tscer** = $f_one
- **tin** = $f_tin
- **AggVar_Tolerance** = 1
- **AggVar_Name** = poa
- **yem_a** = $f_hourly_wage
- **Dataset** = 4 variants
- **bchlp** = 0
- **yprrt** = $f_rri
- **yptmp** = $f_hourly_wage
- **bsawk** = $f_bsawk
- **bchba** = $f_bchba
- **ymwdt** = $f_hourly_wage_dt
- **yem20_a** = $f_hourly_wage
- **tscee** = $f_one
- **tscse** = $f_one
- **xed00** = $f_hicp
- **xhl00** = $f_hicp
- **Factor_Condition** = 13 variants
- **yem00** = 13 variants
- **yemxp** = 13 variants
- **xhc** = $f_hicp

## ConstDef_fr / DefConst
- Retirement Age
- **$RetirementAge_Min** = 62
- **const_monetary** = no
- **$RetirementAge_Full** = 67

## ConstDef_fr / DefConst
- Income limits for SIC purposes
- **$IncGrALim** = 3170#m
- **const_monetary** = yes
- **$IncGrBLim** = 12680#m
- **$IncGrCLim** = 25360#m
- **$IncGr1Lim** = 3170#m
- **$IncGr2Lim** = 9510#m
- **$PSS** = 38040#y
- **$Exempt_overtime** = n/a

## ConstDef_fr / DefConst
- Unemployment benefits: bunct
- **$UB_QperMin** = 4
- **const_monetary** = 2 variants
- **$UB_QperTot** = 28
- **$UB_FDA** = 11.76#d
- **$UB_amt_min** = 28.58#d
- **$UB_amt_rt1** = 0.404
- **$UB_amt_rt2** = 0.57
- **$UB_amt_max** = 0.75
- **$ImputedWage** = 0
- **$UB_QperTot_2** = 36
- **$UB_inclt_reg** = n/a

## ConstDef_fr / DefConst
- Unemployment benefits: bunmt
- **$bunmt_amt** = 16.25#d

## ConstDef_fr / DefConst
- Parben: constants
- **$lhw** = 35

## ConstDef_fr / DefConst
- constants for COVID-19 compensation schemes
- **$mc_yem_rrate** = n/a
- **$mc_yem_share** = n/a
- **$mc_yem_min** = n/a
- **$mc_yem_max** = n/a
- **$mc_yse_my** = n/a
- **$mc_yse_amount** = n/a

## IlDef_fr / DefIl
- il_capy: Capital income
- **yiy** = +
- **ypr** = +

## IlDef_fr / DefIl
- il_temp_bun: Unemployment benefits (simulated unemp insurance + data unemp assistance)
- **bunct_s** = +
- **bunmt_s** = +
- **bwkmcee_s** = n/a
- **yemmc_s** = n/a

## IlDef_fr / DefIl
- Taxable pensions
- **poa00** = +
- **pdi00** = +
- **psu** = +
- **ypp** = +

## IlDef_fr / DefIl
- il_dpisilc: Standardized disposable income (SILC definition)
- **ils_earns** = +
- **bunct_s** = +
- **bunmt_s** = +
- **bhl** = +
- **poa00** = +
- **psu** = +
- **bsuwd_s** = +
- **bed** = +
- **pdi00** = +
- **bdi_s** = +
- **ypr** = +
- **yiy** = +
- **ypt** = +
- **yot** = +
- **bhotn_s** = +
- **bhoot** = +
- **bch00_s** = +
- **bchyc_s** = +
- **bchba_s** = +
- **bchcc_s** = +
- **bched_s** = +
- **bchlg_s** = +
- **bsaoa_s** = +
- **bsa00_s** = +
- **bchlp_s** = n/a
- **xmp** = -
- **ils_tax** = -
- **ils_sicee** = -
- **ils_sicse** = -
- **tad** = +
- **bsaeccm_s** = n/a
- **bwkmcee_s** = n/a
- **bwkmcse_s** = n/a
- **bseec_s** = n/a

## IlDef_fr / DefIl
- Tax base for CSG and CRDS: ils_earns excluding yemmc_s
- **yse** = +
- **yem00** = +
- **yemxp** = +

## TUDef_fr / DefTu
- tu_individual_fr
- **Type** = IND
- **DepChildCond** = dag<20 & ( ils_earns< 0.55*(169*$Minwage_hourly) \\

## TUDef_fr / DefTu
- tu_household_fr
- **Type** = HH
- **DepChildCond** = dag < 18

## TUDef_fr / DefTu
- tu_fiscalunit_fr
- **PartnerCond** = default & IsMarried
- **DepChildCond** = default & (dag<21 \\
- **DepRelativeCond** = !IsDepChild & IsDisabled & !IsHead & ! IsPartner
- **LoneParentCond** = Default
- **Members** = Partner& OwnDepchild & LooseDepChild & DepRelative
- **AssignDepChOfDependents** = yes
- **NoChildIfHead** = yes
- **Type** = SUBGROUP

## TUDef_fr / DefTu
- tu_bch_fr: Tax unit for family benefit purposes
- **Type** = SUBGROUP
- **Members** = Partner & OwnDepChild & LooseDepChild
- **DepChildCond** = dag<20 & ils_earns#2<(0.55*(169*$Minwage_hourly))
- **#_Level** = tu_individual_fr
- **AssignDepChOfDependents** = yes
- **LoneParentCond** = IsParentOfDepChild & !IsWithPartner & !IsMarried & nChildrenOfCouple#1>0
- **#_AgeMax** = 17

## TUDef_fr / DefTu
- DEF: ASSESSMENT UNITS
- **type** = HH
- **DepChildCond** = dag<14

## TUDef_fr / DefTu
- tu_bch_fextra_fr:special tax unit for the supplement awarded to 3+ children families when the oldest turns 20
- **Type** = SUBGROUP
- **Members** = Partner & OwnDepChild & LooseDepChild
- **DepChildCond** = dag<21 & ils_earns#2<(0.55*(169*$Minwage_hourly))
- **#_Level** = tu_individual_fr
- **AssignDepChOfDependents** = yes
- **LoneParentCond** = IsParentOfDepChild & !IsWithPartner & !IsMarried & nChildrenOfCouple#1>0
- **#_AgeMax** = 17

## TUDef_fr / DefTu
- special TU for purposes of this benefit
- **DepChildCond** = (dag<20 \\
- **Members** = Partner & OwnDepChild & LooseDepChild
- **Type** = SUBGROUP
- **NoChildIfHead** = yes
- **NoChildIfPartner** = yes

## random_fr / DefVar
- DEF: Random non take-up of RMI/RSA + TransLMA random variables
- **i_takeup** = 0
- **var_monetary** = no
- **i_takeup2** = 0
- **Var_Monetary** = 2 variants
- **i_mc_rand_1** = n/a
- **i_mc_rand_2** = n/a
- **i_mc_rand_3** = n/a
- **i_lma_rand_1** = n/a
- **i_lma_rand_2** = n/a
- **i_lma_rand_3** = n/a

## random_fr / RandSeed
- DEF: Random non take-up of RMI/RSA + TransLMA random variables
- **seed** = 3579

## random_fr / ArithOp
- Simulate non-take up
- **formula** = rand
- **output_var** = i_takeup
- **TAX_UNIT** = tu_bsa00_fr

## random_fr / RandSeed
- DEF: Random non take-up of RMI/RSA + TransLMA random variables
- **Seed** = n/a

## random_fr / ArithOp
- Simulate non-take up
- **formula** = rand
- **output_var** = i_takeup2
- **TAX_UNIT** = tu_bsa00_fr

## random_fr / DefVar
- DEF: Random non take-up of RMI/RSA + TransLMA random variables
- **i_mc_rand_1** = n/a
- **i_mc_rand_2** = n/a
- **i_mc_rand_3** = n/a
- **i_lma1** = n/a
- **i_lma2** = n/a
- **i_lmamy** = n/a

## random_fr / RandSeed
- Random assignment of Loss in Turnover - Covid
- **Seed** = n/a

## random_fr / ArithOp
- uniform random variable for ysecomp_dk
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## random_fr / RandSeed
- random seed 4
- **Seed** = n/a

## random_fr / ArithOp
- uniform random variable 1 for InitVarsLMA
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## random_fr / RandSeed
- random seed 5
- **Seed** = n/a

## random_fr / ArithOp
- uniform random variable 2 for InitVarsLMA
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## random_fr / RandSeed
- random seed 6
- **Seed** = n/a

## neg_fr / Elig
- INC: Adjustment of self-employment income
- **Elig_Cond** = yse!=0
- **TAX_UNIT** = tu_individual_fr

## neg_fr / ArithOp
- INC: Adjustment of self-employment income
- **Who_Must_Be_Elig** = one
- **Formula** = 1
- **Output_Var** = lse_s
- **TAX_UNIT** = tu_individual_fr

## neg_fr / ArithOp
- INC: Adjustment of self-employment income
- **Formula** = max(yse,0)
- **Output_Var** = yse
- **TAX_UNIT** = tu_individual_fr

## yem_fr / Elig
- eligibility: only those with (positive) employment income
- **elig_cond** = yem00 > 0
- **TAX_UNIT** = tu_individual_fr

## yem_fr / Max
- calculate and apply minimum wage
- **who_must_be_elig** = one
- **val** = 2 variants
- **output_var** = yem00
- **TAX_UNIT** = tu_individual_fr

## yem_fr / ChangeParam
- INC: Minimum  wage
- **Param_Id** = 30b6375e-e5da-478d-b9f0-359bd3405ccb
- **Param_NewVal** = FR_2015_yem_std

## bunct_fr / ArithOp
- unemployment duration: baseline
- **formula** = max(lunmy,bunmy)
- **lowlim** = 0
- **output_var** = lunmy_s
- **TAX_UNIT** = tu_individual_fr

## bunct_fr / Elig
- eligibility check
- **elig_cond** = lunmy_s > 0 & liwmy_s >= $UB_QperMin & (dag < 62 \\
- **TAX_UNIT** = tu_individual_fr

## bunct_fr / BenCalc
- benefit duration: basic entitlement (in months)-before 2009
- **comp_cond** = n/a
- **comp_perElig** = n/a
- **Comp_Cond** = n/a
- **Comp_perElig** = n/a
- **LowLim** = n/a
- **UpLim** = n/a
- **output_var** = n/a
- **TAX_UNIT** = n/a

## bunct_fr / BenCalc
- benefit duration: basic entitlement (in months)-after 2009
- **Comp_Cond** = 3 variants
- **Comp_perElig** = liwwh
- **Comp_UpLim** = 3 variants
- **LowLim** = bunmy
- **UpLim** = lunmy_s
- **Output_Var** = bunctmy_s
- **TAX_UNIT** = tu_individual_fr
- **Who_Must_Be_Elig** = one

## bunct_fr / BenCalc
- benefit amount: previous average gross monthly earnings
- **who_must_be_elig** = one
- **comp_cond** = 3 variants
- **comp_perElig** = 3 variants
- **output_var** = yempv_s
- **TAX_UNIT** = tu_individual_fr
- **Comp_perElig** = 0
- **Comp_Cond** = lunmy_s>0 & bunct=0 & lnu=0

## bunct_fr / Max
- benefit amount: per month
- **Who_Must_Be_Elig** = one
- **Val** = 2 variants
- **Output_Var** = bunct_s
- **TAX_UNIT** = tu_individual_fr
- **UpLim** = yempv_s * $UB_amt_max
- **LowLim** = $UB_amt_min
- **Limpriority** = upper

## bunct_fr / ArithOp
- BEN: Unemployment insurance benefit (Allocation de retour à l’emploi ARE): PART SIMULATED
- **Formula** = bunct_s
- **LowLim** = $UB_amt_min
- **UpLim** = yempv_s * $UB_amt_max
- **limpriority** = upper
- **Output_Var** = bunct_s
- **TAX_UNIT** = tu_individual_fr

## bunct_fr / ArithOp
- benefit amount: average monthly amount per year
- **Formula** = (bunct_s * bunctmy_s) / 12
- **Output_Var** = bunct_s
- **TAX_UNIT** = tu_individual_fr

## bunct_fr / BenCalc
- eligibility: no of months worked in qualifying period
- **comp_cond** = 2 variants
- **comp_perElig** = 2 variants
- **output_var** = liwmy_s
- **TAX_UNIT** = tu_individual_fr
- **Comp_Cond** = 3 variants
- **Comp_perElig** = 2 variants

## bunct_fr / BenCalc
- benefit duration: limit for those in receipt
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = bunctmy_s
- **TAX_UNIT** = tu_individual_fr

## bunct_fr / BenCalc
- reduction for high salaries from 7th month (since December 2021)
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a

## bunct_fr / BenCalc
- 2023: The Compensation period is reduced by 25%.
- **Comp_Cond** = n/a
- **Comp_perElig** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bch00_fr / BenCalc
- Benefit base amount (full rate)
- **Comp_Cond** = 5 variants
- **Comp_perTU** = 2 variants
- **Comp_perElig** = 3 variants
- **#_N** = 2 variants
- **#_M** = 99
- **Output_Var** = bch00_s
- **TAX_UNIT** = tu_bch_fr

## bch00_fr / BenCalc
- Extra benefit amount given to families with 3+ children and a child aged 20
- **comp_cond** = dag=20 & nDepChildrenInTu >=3
- **comp_perTU** = $bch00_amt6
- **output_add_var** = bch00_s
- **TAX_UNIT** = tu_bch_extra_fr

## bch00_fr / Allocate
- Allocate to the mother
- **Share** = bch00_s
- **Share_Between** = (IsParentOfDepChild & dgn=0) \\
- **Output_Var** = bch00_s
- **TAX_UNIT** = tu_bch_extra_fr

## bch00_fr / DefConst
- Constants
- **$bch00_amt1** = 130#m
- **$bch00_amt2** = 296.53#m
- **$bch00_amt3** = 166.55#m
- **$bch00_amt4** = n/a
- **$bch00_amt5** = 64.99#m
- **$bch00_amt6** = 82.19#m
- **$bch00_inclt4** = n/a
- **$bch00_inclt2** = n/a
- **$bch00_inclt1** = n/a
- **$bch00_inclt3** = n/a
- **$bch00_inclt5** = n/a

## bch00_fr / BenCalc
- Total benefit amount
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bchor_fr / BenCalc
- BEN: Family Support Allowance (Allocation de soutien familial ASF)
- **comp_cond** = IsDepChild & (GetMotherInfo#1=5 \\
- **Comp_perElig** = 2 variants
- **output_var** = bchor_s
- **TAX_UNIT** = tu_bch_fr
- **Comp_Cond** = IsLooseDepChild
- **Who_Must_Be_Elig** = all
- **#_Info** = dms

## bchor_fr / DefConst
- ASF paramters
- **$bchor_amt1** = 100.58#m
- **$bchor_amt2** = 134.05#m

## bchor_fr / Elig
- No maintainence allowance received
- **Elig_Cond** = ypt=0
- **TAX_UNIT** = tu_household_fr

## bchor_fr / Elig
- BEN: Family Support Allowance (Allocation de soutien familial ASF)
- **Elig_Cond** = IsLoneParentOfDepChild
- **TAX_UNIT** = tu_bch_fr
- **Output_Var** = i_loneparent

## bchor_fr / DefVar
- BEN: Family Support Allowance (Allocation de soutien familial ASF)
- **i_loneparent** = 0
- **Var_Monetary** = no

## tscee_fr / DefVar
- Intermediate variables
- **i_scee_base** = 0
- **var_monetary** = yes
- **i_yemxp** = n/a
- **Var_Monetary** = n/a
- **i_rateSCyemxp** = n/a

## tscee_fr / DefIl
- il_tscee_base: Income base for employee & employer contributions
- **yemxp** = +
- **yem00** = +

## tscee_fr / SchedCalc
- Sickness insurance contributions
- **Base** = il_tscee_base
- **Band_Rate** = $tsceesi_rt
- **Output_Var** = tsceesi_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / Elig
- Avoid division by 0!!!!
- **Elig_Cond** = il_tscee_base>0
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / ArithOp
- Monthly tax base to be subject to ceilings
- **Who_Must_Be_Elig** = one
- **Formula** = il_tscee_base*12/yemmy
- **Output_Var** = i_scee_base
- **TAX_UNIT** = tu_individual_fr
- **LowLim** = n/a

## tscee_fr / SchedCalc
- Old Age insurance contributions
- **Base** = i_scee_base
- **Band_UpLim** = $IncGrALim
- **Band_Rate** = 2 variants
- **Result_Var** = tsceepi00_s
- **Output_Var** = tsceepi_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / Elig
- Non white collar employee
- **Elig_Cond** = loc!=1 & loc!=2
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / SchedCalc
- Complementary insurance for non white collar
- **Who_Must_Be_Elig** = one
- **Base** = i_scee_base
- **Band_UpLim** = 2 variants
- **Band_Rate** = 2 variants
- **Result_Var** = tsceepibc_s
- **Output_Add_Var** = tsceepi_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / Elig
- White collar employee
- **Elig_Cond** = loc=1 \\
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / SchedCalc
- Complementary insurance for white collar
- **Who_Must_Be_Elig** = one
- **Base** = i_scee_base
- **Band_UpLim** = 3 variants
- **Band_Rate** = 3 variants
- **Result_Var** = tsceepiwc_s
- **Output_Add_Var** = tsceepi_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / SchedCalc
- Outstanding contribution (CET)
- **Base** = i_scee_base
- **Band_UpLim** = $IncGrCLim
- **Band_Rate** = 2 variants
- **Result_Var** = tsceepicp_s
- **Output_Add_Var** = tsceepi_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / BenCalc
- AGFF contribution
- **Comp_Cond** = 3 variants
- **Comp_perElig** = 3 variants
- **Output_Add_Var** = tsceepi_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / BenCalc
- Unemployment insurance contribution
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **Output_Var** = tsceeui_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / ArithOp
- Rescale pensions SICs over 12 months
- **Formula** = tsceepi_s*yemmy/12
- **Output_Var** = tsceepi_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / ArithOp
- Rescale Unemployment SIC over 12 months
- **Formula** = tsceeui_s*yemmy/12
- **Output_Var** = tsceeui_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / ArithOp
- Add employee contributions
- **Formula** = tsceesi_s+ tsceepi_s + tsceeui_s
- **Output_Var** = tscee_s
- **TAX_UNIT** = tu_individual_fr

## tscee_fr / DefConst
- Parameters for employee social insurance contributions
- **$tsceesi_rt** = 0.0075
- **$tsceepi_rt1** = 0.0715
- **$tsceepi_rt2** = 0.0030
- **$tsceepi_rt5** = 0.0310
- **$tsceepi_rt6** = 0.0780
- **$tsceepi_rt3** = 0.0310
- **$tsceepi_rt4** = 0.0810
- **$tsceepi_rt7** = 0.0780
- **$tsceepi_rt8** = 0.0013
- **$tsceepi_rt9** = 0.008
- **$tsceeui_amt** = n/a
- **$tsceeui_rt2** = 0.00024
- **$tsceeui_rt1** = 0.0240
- **$tsceepi_rt11** = 0.009
- **$tsceepi_rt10** = 0.009
- **$tscee_xp** = n/a

## tscer_fr / ArithOp
- Sickness insurance contributions
- **Formula** = il_tscee_base*$tscersi_rt
- **Output_Var** = tscersi_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / ArithOp
- Family insurance contributions
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tscer_fr / ArithOp
- Rescale housing contributions over the year
- **Formula** = tscerho_s *yemmy/12
- **Output_Var** = tscerho_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- Old-age insurance contributions-main
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 4 variants
- **Output_Var** = tscerpi_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- AGFF (old age)
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **Output_Add_Var** = tscerpi_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- Contingency insurance for white collar workers
- **Comp_Cond** = loc=1 \\
- **Comp_perTU** = min(i_scee_base,$IncGrALim)*$tscerot_rt
- **Output_Var** = tscerot_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / ArithOp
- Re-scale Contingency insurance over 12 months
- **Formula** = tscerot_s*yemmy/12
- **Output_Var** = tscerot_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / ArithOp
- Outstanding Contribution (CET)- Complementary pension
- **Formula** = min(i_scee_base,$IncGrCLim)*$tscerpi_rt10
- **Result_Var** = tscerpicp_s
- **Output_Add_Var** = tscerpi_s
- **TAX_UNIT** = tu_individual_fr
- **Who_Must_Be_Elig** = all

## tscer_fr / ArithOp
- Rescale employer pension contributions over the year
- **Formula** = tscerpi_s*yemmy/12
- **Output_Var** = tscerpi_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- Unemployment insurance contributions
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **Output_Var** = tscerui_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / ArithOp
- Rescale employer unemployment insurance contributions over the year
- **Formula** = tscerui_s*yemmy/12
- **Output_Var** = tscerui_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / ArithOp
- Apprenticeship tax
- **Formula** = il_tscee_base*$tscerap_rt
- **Output_Var** = tscerap_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / ArithOp
- Add employer contributions
- **Formula** = tscersi_s+ tscerfa_s + tscerho_s + tscerpi_s + tscerui_s + tscerir_s + tscerot_s+tscerap_s+tsceruf_s-tscerrd_s
- **Output_Var** = tscer_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- FNAL contribution for firms with > 50 employees (20 until 2019)
- **Comp_Cond** = lfs>20
- **Comp_perTU** = i_scee_base*$tscerho_rt2
- **Output_Add_Var** = tscerho_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- Professional training contribution
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **Output_Add_Var** = tscerir_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- Participation in the reconstruction effort
- **Comp_Cond** = lfs>=20
- **Comp_perTU** = il_tscee_base*$tscerir_rt1
- **Output_Var** = tscerir_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- Calculate applicable reduction coefficient
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = i_tscerrd_coef
- **TAX_UNIT** = tu_individual_fr
- **Who_Must_Be_Elig** = all
- **Comp_UpLim** = $tscer_coef1

## tscer_fr / DefConst
- Reduction coefficient
- **$tscer_coef1** = 0.2795
- **$tscer_coef2** = 0.2835
- **$tscerpi_rt1** = 0.085
- **$tscerho_rt2** = 0.005
- **$tscerho_rt1** = 0.001
- **$tscerfa_rt** = 0.0525
- **$tscersi_rt** = 0.128
- **$tscerpi_rt7** = 0.1275
- **$tscerpi_rt6** = 0.0465
- **$tscerpi_rt5** = 0.1215
- **$tscerpi_rt4** = 0.0465
- **$tscerpi_rt3** = 0.003
- **$tscerpi_rt2** = 0.018
- **$tscerpi_rt8** = 0.012
- **$tscerui_rt2** = 0.00036
- **$tscerui_rt1** = 0.04
- **$tscerot_rt** = 0.015
- **$tscerpi_rt10** = 0.0022
- **$tscerpi_rt9** = 0.013
- **$tscerir_rt3** = 0.0105
- **$tscerir_rt2** = 0.0055
- **$tscerir_rt1** = 0.0045
- **$tscerap_rt** = 0.0068
- **$tscerui_amt** = n/a
- **$tscerir_rt4** = 0.016
- **$tsceruf_rt** = 0.00016
- **$tscersi_rt2** = n/a
- **$tscerfa_rt2** = 0.0345

## tscer_fr / Elig
- Companies with less than 50 employees (20 until 2019)
- **Elig_Cond** = lfs<20
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / Elig
- Companies with 50 employees or more (20 until 2019)
- **Elig_Cond** = lfs>=20
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- Calculate applicable reduction coefficient
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Add_Var** = i_tscerrd_coef
- **TAX_UNIT** = tu_individual_fr
- **Who_Must_Be_Elig** = all
- **Comp_UpLim** = $tscer_coef2

## tscer_fr / DefVar
- SIC: Employer Social Insurance Contributions
- **i_tscerrd_coef** = 0
- **i_scer_base** = n/a
- **i_tscerrdglob_coef** = n/a

## tscer_fr / ArithOp
- Calculate final amount of employer sic reduction
- **Formula** = i_tscerrd_coef*il_tscee_base
- **Output_Var** = tscerrd_s
- **TAX_UNIT** = tu_individual_fr
- **UpLim** = ils_sicer

## tscer_fr / BenCalc
- Housing insurance contributions
- **Comp_Cond** = lfs<=20
- **Comp_perTU** = $tscerho_rt1*min(i_scee_base,$IncGrALim)
- **Output_Var** = tscerho_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / Elig
- Outstanding contribution- only for white colalr workers
- **Elig_Cond** = loc=1 \\
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / ArithOp
- Contribution to unions and professional organizations
- **Formula** = il_tscee_base*$tsceruf_rt
- **Output_Var** = tsceruf_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- SIC: Employer Social Insurance Contributions
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tscer_fr / BenCalc
- entitlement to reductions in employers’ social security contributions (Fillon reduction) AGIRC ARRCO (part of old-age insurance contributions and incl in tscerpi_s)
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tscer_fr / BenCalc
- entitlement to reductions in employers’ social security contributions (Fillon reduction) AAGFF - CEG (part of old-age insurance contributions and incl in tscerpi_s)
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tscer_fr / Elig
- SIC: Employer Social Insurance Contributions
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## tscer_fr / ArithOp
- SIC: Employer Social Insurance Contributions
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tscer_fr / BenCalc
- SIC: Employer Social Insurance Contributions
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = tscerfa_s
- **TAX_UNIT** = tu_individual_fr

## tscer_fr / BenCalc
- Additional Reduction- Calculate applicable reduction coefficient
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tscer_fr / ArithOp
- SIC: Employer Social Insurance Contributions
- **Formula** = n/a
- **UpLim** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a

## tscse_fr / ArithOp
- Family Benefits-SIC
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tscse_fr / Elig
- Agricultural self-employment
- **Elig_Cond** = lindi=1
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / Elig
- ARTISAN: Artisans
- **Elig_Cond** = loc=7 & lindi!=1 & lse_s=1
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / SchedCalc
- ARTISAN: Sickness insurance contributions for artisans / UNTIL 2016
- **Who_Must_Be_Elig** = one
- **Base** = yse#1
- **#_lowlim** = 0.4*$PSS
- **Band_UpLim** = n/a
- **Band_Rate** = 2 variants
- **Output_Add_Var** = tscsesi_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / SchedCalc
- ARTISAN: Supplementary sickness insurance contribution
- **who_must_be_elig** = one
- **base** = yse#1
- **#_lowlim** = 0.4*$PSS
- **band_rate** = $tscsesi_rt4
- **band_uplim** = 5*$PSS
- **output_add_var** = tscsesi_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / Elig
- INDUSTRY & TRADE: Industry & trade
- **Elig_Cond** = loc!= 7 & lindi!=1 & lse_s=1
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / SchedCalc
- I&T: Sickness insurance contributions for industry & trade / UNTIL 2016
- **Who_Must_Be_Elig** = one
- **Base** = yse#1
- **#_lowlim** = 0.4*$PSS
- **Band_UpLim** = n/a
- **Band_Rate** = 2 variants
- **Output_Add_Var** = tscsesi_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / SchedCalc
- I&T: Supplementary sickness insurance contribution
- **who_must_be_elig** = one
- **base** = yse#1
- **#_lowlim** = 0.4*$PSS
- **band_rate** = $tscsesi_rt4
- **band_uplim** = 5*$PSS
- **output_add_var** = tscsesi_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / Elig
- FARMER: Agricultural self-employment
- **Elig_Cond** = lindi=1 & lse_s=1
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / SchedCalc
- FARMER: Pensions insurance contributions in the agricultural sector ( MAIN)
- **Who_Must_Be_Elig** = one
- **Base** = yse
- **Band_UpLim** = $PSS
- **Band_Rate** = 2 variants
- **Output_Var** = tscsepi00_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / ArithOp
- FARMER:Complementary pension insurance for the agricultural sector
- **Who_Must_Be_Elig** = one
- **Formula** = yse*$tscsepi_rt3
- **Output_Var** = tscsepicp_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / Elig
- ARTISAN & I&T: Self-employment: artisans & industry & trade
- **Elig_Cond** = lindi!=1 & lse_s=1
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / SchedCalc
- ARTISAN & I&T:Pension insurance contributions for artisans & industry & trade (MAIN)
- **Who_Must_Be_Elig** = one
- **Base** = yse#1
- **Band_UpLim** = $PSS
- **Band_Rate** = 2 variants
- **Output_Add_Var** = tscsepi00_s
- **TAX_UNIT** = tu_individual_fr
- **#_LowLim** = 0.077*$PSS

## tscse_fr / Elig
- ARTISAN: Artisans
- **Elig_Cond** = lindi!=1 & loc=7& lse_s=1
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / SchedCalc
- ARTISAN: Complementary pension insurance contributions for artisans
- **Who_Must_Be_Elig** = one
- **Base** = yse#1
- **Band_UpLim** = 2 variants
- **Band_Rate** = 2 variants
- **Output_Add_Var** = tscsepicp_s
- **TAX_UNIT** = tu_individual_fr
- **#_LowLim** = $PSS*0.0525

## tscse_fr / Elig
- I& T: Industry & trade
- **Elig_Cond** = lindi!=1 & loc!=7 & lse_s=1
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / SchedCalc
- I&T: Complementary pension insurance contributions for industry & trade
- **Who_Must_Be_Elig** = one
- **Base** = yse#1
- **Band_UpLim** = 2 variants
- **Band_Rate** = 2 variants
- **Output_Add_Var** = tscsepicp_s
- **TAX_UNIT** = tu_individual_fr
- **#_LowLim** = 0.0525*$PSS

## tscse_fr / ArithOp
- I&T: Add pension insurance contributions
- **Formula** = tscsepi00_s+tscsepicp_s
- **Output_Var** = tscsepi_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / Elig
- ARTISAN: Artisans
- **Elig_Cond** = lindi!=1 & loc=7 & lse_s=1
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / ArithOp
- ARTISAN: Professional training contribution for artisans
- **who_must_be_elig** = one
- **formula** = $PSS*$tscseir_rt1
- **output_var** = tscseir_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / ArithOp
- ARTISAN:Invalidity and death insurance-for artisans
- **who_must_be_elig** = one
- **formula** = min(yse,$PSS*$tscsedi_rtpss)*$tscsedi_rt1
- **Output_Add_Var** = tscsedi_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / Elig
- I&T: Industry & trade
- **Elig_Cond** = lindi!=1 & loc!=7&lse_s=1
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / ArithOp
- I&T: Professional training contribution for industry and trade
- **who_must_be_elig** = one
- **formula** = $PSS*$tscseir_rt2
- **output_add_var** = tscseir_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / ArithOp
- I&T: Invalidity and death insurance-for industry and trade
- **who_must_be_elig** = one
- **formula** = min(yse,$PSS*$tscsedi_rtpss)*$tscsedi_rt2
- **output_add_var** = tscsedi_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / ArithOp
- Add all self-employed social insurance contributions
- **Formula** = tscsefa_s+ tscsesi_s+ tscsepi_s+tscseir_s+tscsedi_s
- **Output_Var** = tscse_s
- **TAX_UNIT** = tu_individual_fr

## tscse_fr / BenCalc
- I&T: Sickness insurance contributions: reductions for low earners
- **Comp_perTU** = n/a
- **Comp_Cond** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a
- **Who_Must_Be_Elig** = n/a

## tscse_fr / BenCalc
- Family Benefits-SIC (travailleurs indépendants)
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **Output_Var** = tscsefa_s
- **TAX_UNIT** = tu_individual_fr
- **Who_Must_Be_Elig** = one

## tscse_fr / BenCalc
- Family benefits-SIC
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **Output_Add_Var** = tscsefa_s
- **TAX_UNIT** = tu_individual_fr
- **Who_Must_Be_Elig** = one

## tscse_fr / DefConst
- Parameters for self-employed contributions
- **$tscsefa_rt1** = 0.0525
- **$tscsefa_rt2** = 0.0215
- **$tscsefa_rt3** = 0.0345
- **$tscsesi_rt1** = 0.1084
- **$tscsesi_rt2** = 0.065
- **$tscsesi_rt3** = n/a
- **$tscsesi_rt4** = 0.007
- **$tscsepi_rt1** = 0.1467
- **$tscsepi_rt2** = 0.0194
- **$tscsepi_rt3** = 0.03
- **$tscseir_rt1** = 0.0025
- **$tscsepi_rt8** = 0.070
- **$tscsepi_rt7** = 0.080
- **$tscsepi_rt6** = 0.070
- **$tscsepi_rt5** = 0.0035
- **$tscsepi_rt4** = 0.1705
- **$tscseir_rt2** = 0.0025
- **$tscsedi_rt1** = 0.013
- **$tscsedi_rt2** = 0.013
- **$tscsesi_rt5** = n/a
- **$tscsesi_rt10** = n/a
- **$tscsesi_rt9** = n/a
- **$tscsesi_rt8** = n/a
- **$tscsesi_rt7** = n/a
- **$tscsesi_rt6** = n/a
- **$tscsepi_uplim** = 37513#y
- **$tscsedi_rtpss** = 0.20
- **$tscsedi_rt3** = n/a
- **$tscsesi_rt11** = n/a

## tscse_fr / BenCalc
- FARMER: Sickenss insurance contributions for workers in the agricultural sector
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = tscsesi_s
- **TAX_UNIT** = tu_individual_fr
- **Who_Must_Be_Elig** = one
- **Comp_perElig** = n/a

## tscse_fr / BenCalc
- ARTISAN: Sickness insurance contributions for artisans / FROM 2017
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a
- **Who_Must_Be_Elig** = n/a
- **Comp_UpLim** = n/a
- **Comp_LowLim** = n/a

## tscse_fr / BenCalc
- I&T: Sickness insurance contributions / FROM 2017
- **Comp_perTU** = n/a
- **Comp_Cond** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a
- **Who_Must_Be_Elig** = n/a

## tscse_fr / ArithOp
- FARMER:Invalidity and death insurance-for farmers
- **who_must_be_elig** = one
- **formula** = 0
- **output_var** = tscsedi_s
- **TAX_UNIT** = tu_individual_fr

## tsckt_fr / ArithOp
- Liability
- **Formula** = il_capy * ($tsckt_sc + $tsckt_ad + $tsckt_sol)
- **Output_Var** = tsckt_s
- **TAX_UNIT** = tu_individual_fr
- **LowLim** = 0

## tsckt_fr / DefConst
- Policy parameters
- **$tsckt_sc** = 0.0450
- **$tsckt_ad** = 0.003
- **$tsckt_sol** = 0.02
- **$tsckt_sl** = n/a

## bsuwd_fr / DefIl
- Eligibility: Income against which means-test is carried out
- **ils_earns** = +
- **il_capy** = +
- **bdi** = +
- **poa** = +
- **il_temp_bun** = +
- **bhl** = +
- **pdi** = +
- **psu** = +
- **ypp** = +

## bsuwd_fr / Elig
- "Eligibility: Income, age and marital status conditions"
- **Elig_Cond** = il_bsuwd_base<$bsuwd_inclt & dag<55 & dms=5
- **TAX_UNIT** = tu_individual_fr

## bsuwd_fr / ArithOp
- Monthly Benefit Amount
- **Who_Must_Be_Elig** = one
- **Formula** = $bsuwd_amt
- **Output_Var** = bsuwd_s
- **TAX_UNIT** = tu_individual_fr

## bsuwd_fr / DefConst
- BEN: Means-tested benefit for widows/widowers (Allocation veuvage AV)
- **$bsuwd_inclt** = 752.65#m
- **$bsuwd_amt** = 602.12#m

## tinty_fr / DefVar
- Intermediate variables
- **i_rngy** = 0
- **var_monetary** = yes
- **i_rngy_kt** = 0
- **i_yempv** = 0
- **Var_Monetary** = yes

## tinty_fr / BenCalc
- Compute QF
- **Comp_Cond** = 7 variants
- **Comp_perElig** = 2 variants
- **#_N** = 2 variants
- **#_M** = 2 variants
- **Output_Var** = tinqt_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tinty_fr / BenCalc
- Tax deductions/ allowances for C1 income
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **comp_lowlim** = 3 variants
- **comp_uplim** = 3 variants
- **Output_Var** = tintace_s
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / ArithOp
- Deduction on rent income
- **formula** = 0.3*ypr
- **output_var** = tintart_s
- **TAX_UNIT** = tu_individual_fr
- **Who_Must_Be_Elig** = all

## tinty_fr / BenCalc
- Deductions on investment income
- **comp_cond** = 2 variants
- **comp_perTU** = yiy*$tin_tinkt_ded1
- **uplim** = yiy
- **output_var** = tintadt_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tinty_fr / DefIl
- Global Gross Revenue
- **yemxp** = +
- **i_yempv** = +
- **bhl** = +
- **bunct_s** = +
- **bunmt_s** = +
- **il_tscxc_pen** = +
- **yse** = +
- **yiy** = +
- **ypr** = +
- **bsuwd_s** = +
- **ils_sicee** = -
- **ils_sicse** = -
- **tintace_s** = -
- **tscxcktrd_s** = -
- **tscxcnkrd_s** = -
- **tintart_s** = -
- **tintadt_s** = -
- **yemxp_s** = n/a
- **yem00** = n/a
- **yemmc_s** = n/a
- **bwkmcee_s** = n/a

## tinty_fr / BenCalc
- Calculate tax allowance for ascendants & children over 18
- **comp_cond** = 2 variants
- **comp_perElig** = $tin_tintadp
- **output_var** = tintadp_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tinty_fr / BenCalc
- Tax deduction for private pension contributions
- **comp_cond** = xpp>0
- **comp_perTU** = 0.1*(i_yempv+yse-tintace_s)
- **comp_lowlim** = min(xpp,$tin_xppded_min)
- **comp_uplim** = $tin_xppded_max
- **output_var** = tintapv_s
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / DefIl
- Global Net Income
- **il_rgby** = +
- **xmp** = -
- **tintadp_s** = -
- **tintapv_s** = -

## tinty_fr / BenCalc
- Special Deductions for disabled people
- **Comp_Cond** = 2 variants
- **Comp_perElig** = 2 variants
- **Output_Var** = tintadb_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tinty_fr / DefIl
- Net taxable income
- **il_rngy** = +
- **tintadb_s** = -

## tinty_fr / DefIl
- Special taxable income list excluding capital income
- **il_rniy** = +
- **il_capy** = -
- **tscxcktrd_s** = +
- **tintart_s** = +
- **tintadp_s** = +

## tinty_fr / DefIl
- Net taxable income for purposes of benefit eligibility (After 2009)
- **il_rniy** = +
- **yemxp** = n/a

## tinty_fr / DefConst
- Parameters for determining net taxable income (RNI)
- **$tinty_ce_min_yem** = 426#y
- **$tinty_ce_max** = 12157#y
- **$tinty_ce_min_bun** = 936#y
- **$tinty_ce_min_pen** = 379#y
- **$tinty_ce_max_pen** = 3707#y
- **$tscxc_kt_ded** = 0.051
- **$tscxc_yem_ded** = 0.051
- **$tscxc_pen_ded2** = n/a
- **$tscxc_bun_ded** = 0.038
- **$tscxc_bhl_ded** = 0.038
- **$tin_tintadb_lim1** = 14710#y
- **$tin_tintadp** = 3403#y
- **$tin_xppded_max** = 30038#y
- **$tin_xppded_min** = 3755#y
- **$tin_tintadb_amt1** = 2344#y
- **$tin_tintadb_lim2** = 23700#y
- **$tin_tintadb_amt2** = 1172#y
- **$tin_tinkt_ded2** = n/a
- **$tin_tinkt_ded1** = 0.4
- **$tin_tinkt_ded3** = n/a
- **$tinty_ce_max_bun** = 12157#y
- **$csg_thresh1** = 10633#y
- **$csg_thresh2** = 2839#y
- **$csg_thresh3** = 13900#y
- **$csg_thresh4** = 3711#y
- **$csg_thresh5** = n/a
- **$csg_thresh6** = n/a
- **$csg_thresh_red** = $PSS * 4
- **$csg_red** = 0.0175
- **$tscxc_pen_ded1** = 0.038
- **$tscxc_pen_ded3** = 0.042

## tinty_fr / Elig
- Income limit for the deduction on property income to apply
- **Elig_Cond** = ypr<15000#y
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / ArithOp
- Backrating employment income to better match income year/tax year
- **Formula** = 0.985090521831736*yem00
- **Output_Var** = i_yempv
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / ArithOp
- Non-exempted overtime pay (from 2019)
- **Formula** = n/a
- **LowLim** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tinty_fr / ArithOp
- Initialise variable
- **Formula** = 0
- **Output_Var** = tintadb_s
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / ArithOp
- Calculate applicable threshold for exemption of pensions
- **Formula** = $csg_thresh1+((tinqt_s-1)*2*$csg_thresh2)
- **Output_Var** = sin35_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tinty_fr / ArithOp
- Calculate applicable threshold for reduced rate for pensions
- **Formula** = $csg_thresh3+((tinqt_s-1)*2*$csg_thresh4)
- **Output_Var** = sin36_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tinty_fr / ArithOp
- Calculate applicable threshold for median rate for pensions
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tinty_fr / SetDefault
- Default value for a condition for pensions until 2014
- **Dataset** = n/a
- **tin_s** = n/a

## tinty_fr / ArithOp
- Amount of CSG - earnings
- **Formula** = (min(ils_earns, $csg_thresh_red) * (1 - $csg_red) + max(ils_earns - $csg_thresh_red, 0)) * $tscxc_yem_ded
- **LowLim** = 0
- **Output_Var** = tscxcnkrd_s
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / ArithOp
- Amount of CSG - capital income
- **Formula** = il_capy*$tscxc_kt_ded
- **LowLim** = 0
- **Output_Var** = tscxcktrd_s
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / BenCalc
- Amount of CSG - pensions
- **Comp_Cond** = 4 variants
- **Comp_perTU** = 4 variants
- **#_Level** = tu_fiscalunit_fr
- **Output_Add_Var** = tscxcnkrd_s
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / BenCalc
- Amount of CSG - unemployment benefits
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 2 variants
- **#_Level** = tu_fiscalunit_fr
- **Output_Add_Var** = tscxcnkrd_s
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / ArithOp
- Amount of CSG - sickness benefits
- **Formula** = bhl * $tscxc_bhl_ded
- **Output_Add_Var** = tscxcnkrd_s
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / ArithOp
- Amount of CSG - parental leave benefits
- **Formula** = (bmact_s + bpact_s) * $tscxc_bhl_ded
- **Output_Add_Var** = tscxcnkrd_s
- **TAX_UNIT** = tu_individual_fr

## tinty_fr / InitVars
- Init var necessary for MTR add-on
- **bunmt_s** = bunmt

## tscxc_fr / DefConst
- Policy parameters
- **$tscxc_rt1** = 0.075
- **$tscxc_rt2** = 0.066
- **$tscxc_rt3** = 0.062
- **$tscxc_rt4** = 0.082
- **$tscxc_rt5** = 0.062
- **$tscxc_rt6** = n/a
- **$tscxc_rt7** = 0.038
- **$casa_rt** = 0.003

## tscxc_fr / DefVar
- Intermediate variables
- **i_tscxc_earns** = 0
- **i_tscxc_cap** = 0
- **i_tscxc_pen** = 0
- **i_tscxc_unemp** = 0
- **i_tscxc_bhl** = 0
- **i_tscxc_parben** = 0

## tscxc_fr / ArithOp
- Amount of CSG - earnings
- **Formula** = (min(ils_earns_csg, $csg_thresh_red) * (1 - $csg_red) + max(ils_earns_csg - $csg_thresh_red, 0)) * $tscxc_rt1
- **LowLim** = 0
- **Result_Var** = i_tscxc_earns
- **Output_Var** = tscxc_s
- **TAX_UNIT** = tu_individual_fr

## tscxc_fr / ArithOp
- Amount of CSG - capital income
- **Formula** = il_capy*$tscxc_rt4
- **LowLim** = 0
- **Result_Var** = i_tscxc_cap
- **Output_Add_Var** = tscxc_s
- **TAX_UNIT** = tu_individual_fr

## tscxc_fr / BenCalc
- Amount of CSG - pensions
- **Comp_Cond** = 4 variants
- **Comp_perTU** = 4 variants
- **#_Level** = tu_fiscalunit_fr
- **Result_Var** = i_tscxc_pen
- **Output_Add_Var** = tscxc_s
- **TAX_UNIT** = tu_individual_fr

## tscxc_fr / BenCalc
- Amount of CSG - unemployment benefits
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **#_Level** = tu_fiscalunit_fr
- **Result_Var** = i_tscxc_unemp
- **Output_Add_Var** = tscxc_s
- **TAX_UNIT** = tu_individual_fr

## tscxc_fr / ArithOp
- Amount of CSG - sickness benefits
- **Formula** = bhl * $tscxc_rt5
- **Result_Var** = i_tscxc_bhl
- **Output_Add_Var** = tscxc_s
- **TAX_UNIT** = tu_individual_fr

## tscxc_fr / ArithOp
- Amount of CSG - parental leave benefits
- **Formula** = (bmact_s + bpact_s) * $tscxc_rt5
- **Result_Var** = i_tscxc_parben
- **Output_Add_Var** = tscxc_s
- **TAX_UNIT** = tu_individual_fr

## tinkt_fr / DefVar
- Define temporary variables
- **i_tinqtimax** = 0
- **var_monetary** = no
- **i_tinqtdep** = 0
- **i_imax_gt_kt** = 0
- **i_imax_nt_kt** = 0
- **i_tingt_kt** = 0
- **i_tingt1** = 0
- **i_tin_capinc** = n/a

## tinkt_fr / SchedCalc
- Separate capital income taxation: Gross income tax (before any IMAX corrections)
- **Base** = il_rniy_kt
- **Quotient** = tinqt_s
- **Band_UpLim** = 5 variants
- **Band_Rate** = 6 variants
- **Output_Var** = i_tingt_kt
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / BenCalc
- Imax: New QF for calculating Imax (excludes dependents)
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 1
- **Output_Var** = i_tinqtimax
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / SchedCalc
- Imax: New gross tax using new QF
- **Base** = il_rniy_kt
- **Quotient** = i_tinqtimax
- **Band_UpLim** = 5 variants
- **Band_Rate** = 6 variants
- **Output_Var** = i_imax_gt_kt
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / ArithOp
- Imax: Shares of dependents in OF
- **Formula** = tinqt_s-i_tinqtimax
- **LowLim** = 0
- **Output_Var** = i_tinqtdep
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / BenCalc
- Imax: Limit on deductions claimed on behalf of dependents
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = tintalm_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / ArithOp
- Imax: Calculate Imax after capped deductions
- **Formula** = i_imax_gt_kt - tintalm_s
- **LowLim** = 0
- **Output_Var** = i_imax_nt_kt
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / ArithOp
- Imax: select higher gross income tax
- **Formula** = max(i_tingt_kt,i_imax_nt_kt)
- **Output_Var** = i_tingt1
- **LowLim** = 0
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / BenCalc
- Complementary reduction
- **Comp_Cond** = 2 variants
- **Comp_perElig** = 2 variants
- **Output_Var** = sin01_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / ArithOp
- Re-calculate gross tax after complementary reduction
- **Formula** = i_tingt1-sin01_s
- **Output_Var** = i_tingt1
- **LowLim** = 0
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / BenCalc
- Tax rebate (Decote)
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = sin02_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / ArithOp
- Final gross tax to pay on non-capital income
- **Formula** = i_tingt1 -sin02_s
- **LowLim** = 0
- **Output_Var** = i_tingt1
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / BenCalc
- Add flat tax on capital income
- **comp_cond** = il_capy>0
- **comp_perTU** = (il_capy-tscxcktrd_s-tintart_s)*$tin_ktrate
- **lowlim** = 0
- **output_add_var** = i_tingt1
- **TAX_UNIT** = tu_fiscalunit_fr

## tinkt_fr / DefConst
- Paramteres of the income tax
- **$tin_rate1** = 0
- **$tin_rate2** = n/a
- **$tin_rate3** = 0.14
- **$tin_rate4** = 0.3
- **$tin_rate5** = 0.41
- **$tin_rate6** = 0.45
- **$tin_imax_db** = 1504#y
- **$tin_uplim5** = 151956#y
- **$tin_uplim4** = 71754#y
- **$tin_uplim3** = 26764#y
- **$tin_uplim2** = n/a
- **$tin_uplim1** = 9690#y
- **$tin_decote** = 1135#y
- **$tin_imax_wd** = 1680#y
- **$tin_ktrate** = 0.24
- **$tin_imax_deplm2** = 1508#y
- **$tin_imax_deplm1** = 3558#y
- **$tin_decote2** = 1870#y
- **$tin_decote_amount** = n/a
- **$tin_decote2_amount** = n/a
- **$tin_decote_rate** = n/a

## tin_fr / DefVar
- Define temporary variables
- **i_imax_gt_all** = 0
- **i_imax_nt_all** = 0
- **i_tingt_all** = 0
- **i_tingt2** = 0

## tin_fr / SchedCalc
- Gross income tax (before any IMAX corrections)
- **Base** = il_rniy
- **Quotient** = tinqt_s
- **Band_UpLim** = 4 variants
- **Band_Rate** = 5 variants
- **band_uplim** = $tin_uplim5
- **band_rate** = $tin_rate6
- **Output_Var** = i_tingt_all
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / SchedCalc
- Imax: New gross tax using new QF
- **Base** = il_rniy
- **Quotient** = i_tinqtimax
- **Band_UpLim** = 4 variants
- **Band_Rate** = 5 variants
- **band_uplim** = $tin_uplim5
- **band_rate** = $tin_rate6
- **Output_Var** = i_imax_gt_all
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / ArithOp
- Imax: Calculate Imax after capped deductions
- **Formula** = i_imax_gt_all - tintalm_s
- **LowLim** = 0
- **Output_Var** = i_imax_nt_all
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / ArithOp
- Imax: select higher gross income tax
- **Formula** = max(i_tingt_all,i_imax_nt_all)
- **Output_Var** = i_tingt2
- **LowLim** = 0
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / BenCalc
- Complementary reduction
- **Comp_Cond** = 2 variants
- **Comp_perElig** = 2 variants
- **Output_Var** = sin01_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / ArithOp
- Re-calculate gross tax after complementary reduction
- **Formula** = i_tingt2-sin01_s
- **Output_Var** = i_tingt2
- **LowLim** = 0
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / BenCalc
- Tax rebate (Decote)
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = sin02_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / ArithOp
- Final gross tax to pay
- **Formula** = i_tingt2 -sin02_s
- **LowLim** = 0
- **Output_Var** = i_tingt2
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / ArithOp
- Optimize final gross tax to pay
- **formula** = min(i_tingt1,i_tingt2)
- **output_var** = tingt_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / Elig
- Exceptional contributions on high income earners: singles
- **Elig_Cond** = nAdultsInTu=1
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / SchedCalc
- Exceptional contributions on high income earners :singles
- **Base** = (il_rniy_kt+il_capy-tscxcktrd_s-tintart_s)
- **Band_UpLim** = 2 variants
- **Band_Rate** = 3 variants
- **Output_Var** = tinto_s
- **TAX_UNIT** = tu_fiscalunit_fr
- **Who_Must_Be_Elig** = all

## tin_fr / Elig
- Exceptional contributions on high income earners: couples
- **Elig_Cond** = nAdultsInTu>1
- **TAX_UNIT** = tu_fiscalunit_fr

## tin_fr / SchedCalc
- Exceptional contributions on high income earners: couples
- **Base** = (il_rniy_kt+il_capy-tscxcktrd_s-tintart_s)
- **Band_UpLim** = 2 variants
- **Band_Rate** = 3 variants
- **Output_Add_Var** = tinto_s
- **TAX_UNIT** = tu_fiscalunit_fr
- **Who_Must_Be_Elig** = all

## tin_fr / DefConst
- Parameters for exceptional contributions on high income
- **$tinto_rt1** = 0.03
- **$tinto_rt2** = 0.04
- **$tinto_inclt1** = 250000#y
- **$tinto_inclt2** = 500000#y
- **$tinto_inclt3** = 1000000#y

## tin_fr / BenCalc
- Supplementary tax reduction (2017-2019) - calculation
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tin_fr / ArithOp
- Supplementary tax reduction (2017-2019) - deduction
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a
- **LowLim** = n/a

## tintcot_fr / BenCalc
- Tax credit on child care expenses
- **comp_cond** = 2 variants
- **#_AgeMin** = 0
- **#_AgeMax** = 6
- **comp_perTU** = $tintcch_amt
- **#_income** = ils_earns
- **output_var** = tintcch_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tintcot_fr / BenCalc
- Tax credit on mortgage expenses
- **comp_cond** = IsHead & dag<=45
- **comp_perTU** = 0.4*xhcmomi
- **output_var** = tintcmi_s
- **TAX_UNIT** = tu_fiscalunit_fr
- **Run_Cond** = !IsUsedDatabase#1
- **#_DataBasename** = FR_20??_b?

## tintcot_fr / BenCalc
- Tax credit on educational expenses of children
- **comp_cond** = 3 variants
- **comp_perElig** = 3 variants
- **output_var** = tintced_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tintcot_fr / ArithOp
- Tax liability after non-refundable tax credits (& before PPE)
- **formula** = tingt_s-tintcch_s-tintcmi_s-tintced_s
- **lowlim** = 0
- **output_var** = tingt_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tintcot_fr / BenCalc
- Tax credit on mortgage expenses
- **comp_cond** = GetSystemYear-5<=amrym & amrym<=2011
- **comp_perTU** = 0.4*xhcmomi
- **output_var** = tintcmi_s
- **TAX_UNIT** = tu_fiscalunit_fr
- **Run_Cond** = IsUsedDatabase#1
- **#_DataBasename** = FR_20??_b?

## tintcot_fr / DefConst
- Monetary parameters for tax credits
- **$tintcch_amt** = 2300#y
- **$tintced_amt1** = 61#y
- **$tinced_amt2** = 153#y
- **$tintced_amt3** = 183#y

## tintcot_fr / ArithOp
- Net tax liability
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## tintcee_fr / DefVar
- TAX: Refundable tax credit for low earners (Prime Pour L'Emploi)
- **temp_convcoef** = 1
- **var_monetary** = no

## tintcee_fr / BenCalc
- PPE: Employee tax credit: threshold for eligibility
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 2 variants
- **Comp_perElig** = 4490#y
- **Output_Var** = sin03_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tintcee_fr / Elig
- PPE Eligibility: Global gross revenue is under threshold
- **Elig_Cond** = (il_rgby+yemxp)<sin03_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tintcee_fr / BenCalc
- PPE: Conversion coeficient based on numbers of hours worked
- **Who_Must_Be_Elig** = one
- **Comp_Cond** = yem>0
- **Comp_perTU** = 1820/(151.9* yemmy)
- **comp_lowlim** = 1
- **comp_cond** = yse>0
- **comp_perTU** = 360/(30*ysemy)
- **Output_Var** = temp_convcoef
- **TAX_UNIT** = tu_individual_fr

## tintcee_fr / ArithOp
- PPE: Equivalent full-time income of the tax payer
- **Who_Must_Be_Elig** = all
- **Formula** = ils_earns*temp_convcoef
- **Output_Var** = sin04_s
- **TAX_UNIT** = tu_individual_fr

## tintcee_fr / DefConst
- PPE: Define Paramenters for PPE derivation
- **$M** = 3743#y
- **const_monetary** = yes
- **$P0** = 12475#y
- **$P1** = 17451#y
- **$P2** = 24950#y
- **$P3** = 26572#y
- **$ME** = 72#y
- **$MF** = 83#y
- **$ML** = 36#y

## tintcee_fr / Elig
- PPE: singles & couples with two earned revenues
- **Elig_Cond** = (!IsMarried & !IsParentOfDepChild#2) \\
- **#_Income** = ils_earns
- **#_Level** = tu_fiscalunit_fr
- **TAX_UNIT** = tu_individual_fr
- **result_var** = sin15_s

## tintcee_fr / BenCalc
- PPE: Amount corresponding to full time: singles & couples with 2 earned revenues
- **Who_Must_Be_Elig** = one
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **#_Level** = tu_fiscalunit_fr
- **Output_Var** = sin05_s
- **TAX_UNIT** = tu_individual_fr
- **result_var** = sin16_s

## tintcee_fr / Elig
- PPE: Couples with one earned revenue
- **Elig_Cond** = IsWithPartner & IsMarried & GetPartnerIncome#1=0
- **#_Income** = ils_earns
- **TAX_UNIT** = tu_individual_fr
- **result_var** = sin17_s

## tintcee_fr / BenCalc
- PPE: Amount corresponding to full time: one earner couples
- **Who_Must_Be_Elig** = one
- **Comp_Cond** = 4 variants
- **Comp_perTU** = 4 variants
- **#_Level** = tu_fiscalunit_fr
- **Output_Add_Var** = sin05_s
- **TAX_UNIT** = tu_individual_fr
- **result_var** = sin18_s

## tintcee_fr / Elig
- PPE: Lone parents
- **Elig_Cond** = IsParentOfDepChild& !IsMarried
- **TAX_UNIT** = tu_fiscalunit_fr
- **result_var** = sin19_s

## tintcee_fr / BenCalc
- PPE: Ammount corresponding to full time: lone parents
- **Who_Must_Be_Elig** = one
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **#_Level** = tu_fiscalunit_fr
- **Output_Add_Var** = sin05_s
- **TAX_UNIT** = tu_individual_fr
- **result_var** = sin20_s

## tintcee_fr / BenCalc
- PPE: Individual amount
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = tintcee_s
- **TAX_UNIT** = tu_individual_fr

## tintcee_fr / ArithOp
- Final tax to pay
- **Formula** = tingt_s - tintcee_s
- **LowLim** = 0
- **Output_Var** = tin_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tintcee_fr / BenCalc
- Adjust final net tax to pay
- **comp_cond** = tin_s>0 & tin_s<61#y
- **comp_perTU** = (0-tin_s)
- **output_add_var** = tin_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tintcee_fr / ArithOp
- Tax refund when PPE is larger than gross tax
- **Formula** = tintcee_s-tingt_s
- **LowLim** = 0
- **Output_Var** = tinrf_s
- **TAX_UNIT** = tu_fiscalunit_fr

## tintcee_fr / BenCalc
- 2009 tax holiday: calculate net taxable income per unit of QF
- **comp_cond** = n/a
- **comp_perTU** = n/a
- **output_var** = n/a
- **TAX_UNIT** = n/a

## tintcee_fr / Elig
- 2009 tax holiday: determine if tax unit qualifies
- **elig_cond** = n/a
- **TAX_UNIT** = n/a
- **result_var** = n/a

## tintcee_fr / ArithOp
- 2009 tax holiday: apply tax reduction
- **who_must_be_elig** = n/a
- **formula** = n/a
- **output_add_var** = n/a
- **TAX_UNIT** = n/a

## bdi_fr / DefConst
- Constants for disability benefit
- **$bdi_inclt1** = 9605.40#y
- **$bdi_inclt2** = 19210.802#y
- **$bdi_inclt3** = 4802.70#y
- **$bdi_amt1** = 800.45#m
- **$bdi_amt2** = 104.8#m
- **$bdi_disr1** = n/a
- **$bdi_disr2** = n/a

## bdi_fr / DefVar
- Temporary variables
- **i_bdi_inclt** = 0
- **var_monetary** = yes
- **i_ddi_nr** = n/a
- **Var_Monetary** = n/a
- **i_bdi_disregard** = n/a

## bdi_fr / BenCalc
- Means test: limit (temp_bdi_inclt)
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 2 variants
- **Comp_perElig** = $bdi_inclt3
- **Output_Var** = i_bdi_inclt
- **TAX_UNIT** = tu_bch_fr

## bdi_fr / Elig
- Means test: eligibility
- **Elig_Cond** = il_rniy_bens< i_bdi_inclt
- **TAX_UNIT** = tu_bch_fr

## bdi_fr / BenCalc
- Benefit amount
- **Who_Must_Be_Elig** = one
- **Comp_Cond** = (dag > 20 & dag < 62) & (ddi = 1)
- **Comp_perElig** = i_bdi_inclt- il_rniy_bens#1
- **Comp_LowLim** = 0
- **Comp_UpLim** = $bdi_amt1
- **#_LowLim** = 0
- **Output_Var** = bdi_s
- **TAX_UNIT** = tu_individual_fr

## bdi_fr / BenCalc
- Supplement for independent living
- **comp_cond** = bdi_s>0 & (bdi_s=$bdi_amt1 \\
- **comp_perTU** = $bdi_amt2
- **output_add_var** = bdi_s
- **TAX_UNIT** = tu_individual_fr

## bdi_fr / ArithOp
- Number of individuals with disability in the unit
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bdi_fr / BenCalc
- Disregard of income of non-disabled head or partner
- **Comp_Cond** = n/a
- **Comp_perElig** = n/a
- **Output_Var** = n/a
- **#_Level** = n/a
- **TAX_UNIT** = n/a

## bunmt_fr / DefVar
- Temporary variables
- **i_bunmt_inc** = 0

## bunmt_fr / Elig
- Eligibility: (!) only those reporting benefit in data (on by default)
- **Elig_Cond** = bunmt> 0
- **TAX_UNIT** = tu_individual_fr

## bunmt_fr / Elig
- Eligibility: rules (off by default)
- **Elig_Cond** = lunmy_s > bunctmy_s & liwwh > 60 & dag < 62
- **TAX_UNIT** = tu_individual_fr

## bunmt_fr / DefTu
- Unit: couple (tu_bunmt_couple)
- **Type** = SUBGROUP
- **Members** = Partner

## bunmt_fr / ArithOp
- Means-test: couple's taxable income
- **Formula** = il_bunmt
- **LowLim** = 0
- **Output_Var** = i_bunmt_inc
- **TAX_UNIT** = tu_bunmt_couple

## bunmt_fr / BenCalc
- Benefit amount
- **Who_Must_Be_Elig** = one
- **Comp_Cond** = 4 variants
- **Comp_perTU** = 3 variants
- **Output_Var** = bunmt_s
- **TAX_UNIT** = tu_bunmt_couple

## bunmt_fr / BenCalc
- Benefit amount: take account of number of months received
- **Comp_perTU** = 2 variants
- **Comp_Cond** = 2 variants
- **Output_Var** = bunmt_s
- **TAX_UNIT** = tu_individual_fr

## bunmt_fr / DefIl
- Income Means-test
- **il_rniy** = +
- **bunct_s** = -

## bchyc_fr / DefVar
- Temporary variables
- **i_bch_inclt1** = 0
- **i_bch_inclt2** = 0

## bchyc_fr / Elig
- Eligibility: One earner couples (married or cohabiting)
- **Elig_Cond** = IsParentOfDepChild & IsWithPartner & GetPartnerIncome#1 <$bchlg_thresh1
- **#_Income** = ils_earns
- **TAX_UNIT** = tu_bch_fr
- **Result_Var** = sin03_s

## bchyc_fr / BenCalc
- Eligibility: Calculate applicable income threshold : One earner couples
- **Who_Must_Be_Elig** = one_adult
- **Comp_Cond** = 9 variants
- **Comp_perTU** = 6 variants
- **Comp_perElig** = 3 variants
- **#_N** = 4
- **#_M** = 99
- **Output_Var** = i_bch_inclt1
- **TAX_UNIT** = tu_bch_fr
- **#_AgeMin** = 3 variants
- **#_AgeMax** = 3 variants

## bchyc_fr / Elig
- Eligibility: Two earner couples & lone parents
- **Elig_Cond** = IsParentOfDepChild & ((IsWithPartner & GetPartnerIncome#1 >=$bchlg_thresh1) \\
- **#_Income** = ils_earns
- **TAX_UNIT** = tu_bch_fr
- **Result_Var** = sin04_s

## bchyc_fr / BenCalc
- Eligibility: Calculate applicable income threshold : Two earner couples and lone parents
- **Who_Must_Be_Elig** = all_adults
- **Comp_Cond** = 9 variants
- **Comp_perTU** = 7 variants
- **#_N** = 4
- **#_M** = 99
- **Comp_perElig** = 3 variants
- **Output_Add_Var** = i_bch_inclt1
- **TAX_UNIT** = tu_bch_fr
- **#_AgeMin** = 3 variants
- **#_AgeMax** = 3 variants

## bchyc_fr / Elig
- Eligibility: Conditions to receive the (full) benefit (amount per family)
- **Elig_Cond** = ((il_rniy_bens< i_bch_inclt1 & dag>1) \\
- **TAX_UNIT** = tu_bch_fr

## bchyc_fr / ArithOp
- Amount: Benefit amount pe eligible family
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bchyc_fr / BenCalc
- Benefit amount: Calculate applicable ceiling to receive the higher amount :one earner couples (only since 2014)
- **Comp_Cond** = 5 variants
- **Comp_perTU** = 4 variants
- **Output_Var** = i_bch_inclt2
- **TAX_UNIT** = tu_bch_fr
- **Who_Must_Be_Elig** = one_adult
- **Comp_perElig** = 2 variants
- **#_M** = 99
- **#_N** = 4
- **#_AgeMax** = 2 variants
- **#_AgeMin** = 2 variants

## bchyc_fr / BenCalc
- Benefit amount: Calculate applicable ceiling to receive the higher amount :two earner couples and lone parents (only since 2014)
- **Comp_Cond** = 5 variants
- **Comp_perTU** = 4 variants
- **Output_Add_Var** = i_bch_inclt2
- **TAX_UNIT** = tu_bch_fr
- **Who_Must_Be_Elig** = all_adults
- **Comp_perElig** = 2 variants
- **#_M** = 99
- **#_N** = 4
- **#_AgeMax** = 2 variants
- **#_AgeMin** = 2 variants

## bchyc_fr / Elig
- Eligibility to receive the lower amount (for children born in 2014 or later)
- **Elig_Cond** = dag<=1 & il_rniy_bens<i_bch_inclt1 & bchyc_s=0
- **TAX_UNIT** = tu_bch_fr

## bchyc_fr / ArithOp
- BEN: Base amount of means-tested benefit for young children (Prestation d´Accueil du Jeune Enfant PAJE)
- **Formula** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a
- **Who_Must_Be_Elig** = n/a

## bchyc_fr / DefConst
- Parameters for PAJE
- **$bchyc_inclt1** = 35729#y
- **$bchyc_inclt5** = 47217#y
- **$bchyc_inclt4** = 8575#y
- **$bchyc_inclt3** = 51450#y
- **$bchyc_inclt2** = 42875#y
- **$bchyc_inclt10** = 6443#y
- **$bchyc_inclt9** = 48615#y
- **$bchyc_inclt8** = 42172#y
- **$bchyc_inclt7** = 62938#y
- **$bchyc_inclt6** = 54363#y
- **$bchyc_inclt15** = 45393#y
- **$bchyc_inclt14** = 5393#y
- **$bchyc_inclt13** = 40693#y
- **$bchyc_inclt12** = 35300#y
- **$bchyc_inclt11** = 29907#y
- **$bchyc_inclt18** = 37996#y
- **$bchyc_inclt17** = 58279#y
- **$bchyc_inclt16** = 51836#y
- **$bchyc_amt1** = 185.54#m
- **$bchyc_inclt20** = 48782#y
- **$bchyc_inclt19** = 43389#y
- **$bchyc_inclt1_2014** = 35729#y
- **$bchyc_inclt34** = n/a
- **$bchyc_inclt33** = n/a
- **$bchyc_inclt32** = n/a
- **$bchyc_inclt31** = n/a
- **$bchyc_inclt30** = n/a
- **$bchyc_inclt29** = n/a
- **$bchyc_inclt28** = n/a
- **$bchyc_inclt27** = n/a
- **$bchyc_inclt26** = n/a
- **$bchyc_inclt25** = n/a
- **$bchyc_inclt24** = n/a
- **$bchyc_inclt23** = n/a
- **$bchyc_inclt22** = n/a
- **$bchyc_inclt21** = n/a
- **$bchyc_amt2** = n/a
- **$bchlg_thresh1** = 5036#y

## bchyc_fr / BenCalc
- BEN: Base amount of means-tested benefit for young children (Prestation d´Accueil du Jeune Enfant PAJE)
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = bchyc_s
- **TAX_UNIT** = tu_bch_fr
- **Who_Must_Be_Elig** = one

## bchyc_fr / BenCalc
- BEN: Base amount of means-tested benefit for young children (Prestation d´Accueil du Jeune Enfant PAJE)
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Add_Var** = bchyc_s
- **TAX_UNIT** = tu_bch_fr
- **Who_Must_Be_Elig** = one

## bchba_fr / Elig
- Eligibility: Conditions
- **Elig_Cond** = il_rniy_bens < i_bch_inclt1 & dag=0
- **TAX_UNIT** = tu_bch_fr

## bchba_fr / ArithOp
- Benefit: Amount
- **Who_Must_Be_Elig** = one
- **Formula** = $bchba_amt1
- **Output_Var** = bchba_s
- **TAX_UNIT** = tu_bch_fr

## bchba_fr / DefConst
- BEN: Baby bonus part of PAJE
- **$bchba_amt1** = 927.71#y
- **$bchba_amt2** = n/a

## bchba_fr / ArithOp
- only if data is older than FR_2017_a1, from FR_2017_a? bchba is disaggregated from bchot
- **Formula** = bchot-bchba_s
- **Output_Var** = bchot_s
- **TAX_UNIT** = tu_individual_fr
- **Run_Cond** = IsUsedDatabase#1 \\
- **#_DataBasename** = 5 variants
- **LowLim** = 0

## bchba_fr / ArithOp
- from FR_2017_a? bchba is disaggregated from bchot so no need to subtract it from bchot
- **Formula** = bchot
- **Output_Var** = bchot_s
- **TAX_UNIT** = tu_individual_fr
- **Run_Cond** = IsUsedDatabase#1 \\
- **#_DataBasename** = 4 variants

## bchcc_fr / DefVar
- Define temporary variables
- **i_bchcc_amt** = 0

## bchcc_fr / ArithOp
- Initialize final output variable
- **formula** = 0
- **output_var** = bchcc_s
- **TAX_UNIT** = tu_individual_fr

## bchcc_fr / Elig
- Optional CLCA /PreParE Majoree: eligibility
- **elig_cond** = liwwh>=24 & ils_earns=0 & bunct_s=0 & bunmt_s=0 & bhl=0
- **TAX_UNIT** = tu_individual_fr

## bchcc_fr / BenCalc
- PreParE Majorée: amount
- **who_must_be_elig** = one
- **comp_cond** = 2 variants
- **#_AgeMin** = 0
- **#_AgeMax** = 0
- **comp_perTU** = $bchcc_amt1*8/12
- **output_add_var** = bchcc_s
- **TAX_UNIT** = tu_bch_fr
- **Comp_perTU** = $bchcc_amt1*4/12
- **Comp_Cond** = 2 variants

## bchcc_fr / Elig
- CLCA/PreParE: eligibility
- **elig_cond** = liwwh>=24 & bunct_s=0& bunmt_s=0 & bhl=0
- **TAX_UNIT** = tu_individual_fr

## bchcc_fr / BenCalc
- CLCA/PreParE: calculate monthly benefit amount based on work reduction conditions
- **who_must_be_elig** = one
- **comp_cond** = 6 variants
- **#_level** = tu_bch_fr
- **comp_perTU** = 6 variants
- **output_var** = i_bchcc_amt
- **TAX_UNIT** = tu_individual_fr
- **#_AgeMin** = 2
- **#_AgeMax** = 2

## bchcc_fr / Elig
- CLCA/PreParE: amount at the family unit level
- **elig_cond** = HasMaxValInTu#1
- **#_unique** = yes
- **#_adults_only** = yes
- **#_val** = i_bchcc_amt
- **TAX_UNIT** = tu_bch_fr

## bchcc_fr / ArithOp
- CLCA/PreParE: amount at the family unit level
- **formula** = sel_s*i_bchcc_amt
- **output_var** = i_bchcc_amt
- **TAX_UNIT** = tu_individual_fr

## bchcc_fr / BenCalc
- Note : benefit also incompatible with bhl & bma & paid holidays; not simulated here
- **comp_cond** = 2 variants
- **comp_perTU** = 2 variants
- **output_add_var** = bchcc_s
- **TAX_UNIT** = tu_bch_fr
- **Comp_perTU** = 2 variants
- **Comp_Cond** = 2 variants
- **#_AgeMin** = 2 variants
- **#_AgeMax** = 3 variants

## bchcc_fr / DefConst
- CLCA/PreParE Paramters
- **$bchcc_amt1** = 641.54#m
- **$bchcc_amt2** = n/a
- **$bchcc_amt4** = 579.12#m
- **$bchcc_amt3** = 392.47#m
- **$bchcc_amt8** = 333.01#m
- **$bchcc_amt7** = 146.36#m
- **$bchcc_amt6** = 440.36#m
- **$bchcc_amt5** = 253.72#m

## bchcc_fr / Allocate
- Allcate to person receving the benefit
- **Share** = bchcc_s
- **Output_Var** = bchcc_s
- **TAX_UNIT** = tu_bch_fr
- **Share_Between** = sel_s=1

## bched_fr / DefVar
- Temporary variables
- **i_bched_inclt** = 0
- **i_bched_amt** = 0

## bched_fr / BenCalc
- Eligibility: Calculate applicable income threshold
- **Comp_Cond** = 4 variants
- **Comp_perTU** = 3 variants
- **#_N** = 4
- **#_M** = 99
- **Comp_perElig** = $bched_inclt4
- **Output_Var** = i_bched_inclt
- **TAX_UNIT** = tu_bch_fr

## bched_fr / BenCalc
- Amount: Benefit amount (before 2012)
- **Comp_Cond** = n/a
- **Comp_perElig** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bched_fr / BenCalc
- Amount: Benefit amount (after 2012)
- **comp_cond** = 3 variants
- **comp_perElig** = 3 variants
- **output_var** = i_bched_amt
- **TAX_UNIT** = tu_bch_fr

## bched_fr / BenCalc
- Amount: Benefit amount (after 2012)
- **comp_cond** = il_rniy_bens<(i_bched_amt+i_bched_inclt)
- **comp_perTU** = i_bched_amt
- **withdraw_base** = max(il_rniy_bens,0)
- **withdraw_start** = i_bched_inclt
- **withdraw_rate** = 1
- **output_var** = bched_s
- **TAX_UNIT** = tu_bch_fr

## bched_fr / BenCalc
- Minimum payment
- **Comp_perTU** = max(bched_s,15#y)
- **Comp_Cond** = bched_s>0
- **Output_Var** = bched_s
- **TAX_UNIT** = tu_bch_fr

## bched_fr / DefConst
- Parameters for ARS
- **$bched_inclt1** = 24306#y
- **$bched_inclt2** = 29915#y
- **$bched_inclt3** = 35524#y
- **$bched_inclt4** = 5609#y
- **$bched_amt1** = 364.45#y
- **$bched_amt2** = 384.53#y
- **$bched_amt3** = 397.88#y

## bchlg_fr / DefConst
- Constants
- **$bchlg_inclt1** = 37555#y
- **$bchlg_inclt2** = 6259#y
- **$bchlg_inclt3** = 45941#y
- **$bchlg_amt1** = 169.19#m
- **$bchlg_inclt6** = 22972#y
- **$bchlg_inclt5** = 3130#y
- **$bchlg_inclt4** = 18779#y
- **$bchlg_amt2** = 203.06#m
- **$bchlg_thresh1** = 5036#y

## bchlg_fr / DefVar
- Temporary variables
- **i_bchlg_nwa** = 0
- **var_monetary** = no
- **i_bchlg_inclt1** = 0
- **i_bchlg_inclt2** = 0

## bchlg_fr / DefTu
- Special TU for this benefit
- **Type** = SUBGROUP
- **DepChildCond** = dag<21 & ils_earns#1<(0.55*(169*$Minwage_hourly))
- **Members** = Partner& OwnDepChild & LooseDepChild
- **#_Level** = tu_individual_fr
- **AssignDepChOfDependents** = yes

## bchlg_fr / BenCalc
- Income test: number of earning partners in unit
- **Comp_Cond** = IsParentOfDepChild & ils_earns#1>$bchlg_thresh1
- **#_Level** = tu_individual_fr
- **Comp_perElig** = 1
- **Output_Var** = i_bchlg_nwa
- **TAX_UNIT** = tu_bchlg_fr

## bchlg_fr / BenCalc
- Income test: first ceiling
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = i_bchlg_inclt1
- **TAX_UNIT** = tu_bchlg_fr

## bchlg_fr / Elig
- Eligibility: conditions to receive the benefit
- **Elig_Cond** = nDepChInTu#1>=3 & bchyc_s=0& bchcc_s=0
- **#_AgeMin** = 3
- **TAX_UNIT** = tu_bchlg_fr

## bchlg_fr / ArithOp
- Benefit Amount (Before 2014)
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bchlg_fr / BenCalc
- Income test: second ceiling
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = i_bchlg_inclt2
- **TAX_UNIT** = tu_bchlg_fr

## bchlg_fr / BenCalc
- Benefit Amount (After 2014)
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = bchlg_s
- **TAX_UNIT** = tu_bchlg_fr
- **Who_Must_Be_Elig** = all

## bhotn_fr / DefVar
- Define temporary variables
- **i_bho_l_lt** = 0
- **i_bho_c** = 0
- **i_bho_l** = 0
- **i_bho_tf** = 0
- **i_bho_rentbase** = 0
- **i_bho_p0** = 0
- **i_bho_tp** = 0
- **i_bho_rl** = 0
- **i_bho_rate** = 0
- **i_bho_minrate** = 0
- **i_bho_r0** = 0
- **i_bho_pp** = 0
- **i_nDepRel** = 0

## bhotn_fr / DefTu
- tu_bho_fr
- **Type** = HH
- **DepChildCond** = dag<21 & ils_earns#1<(0.55*(169*$Minwage_hourly))
- **#_Level** = tu_individual_fr
- **NoChildIfHead** = yes
- **NoChildIfPartner** = yes

## bhotn_fr / BenCalc
- Number of dependents in the unit
- **Comp_Cond** = !IsPartner&!IsHead & (IsDepChild \\
- **Comp_perElig** = 1
- **#_Level** = tu_individual_fr
- **Output_Var** = i_nDepRel
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / BenCalc
- Benefit Amount: (L) Calculate applicable rent limit
- **Comp_Cond** = 15 variants
- **Comp_perTU** = 15 variants
- **Output_Var** = i_bho_l_lt
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / ArithOp
- Benefit Amount: (L) Rent taken into account when awarding the benefit
- **Formula** = xhcrt
- **UpLim** = i_bho_l_lt
- **Output_Var** = i_bho_l
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / BenCalc
- Benefit amount: (C) Lump-sum charge
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **Output_Var** = i_bho_c
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / BenCalc
- Benefit amount: (Pp) Personal participation rate - Tf
- **Comp_Cond** = 8 variants
- **Comp_perTU** = 8 variants
- **LowLim** = 0
- **Output_Var** = i_bho_tf
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / BenCalc
- Benefit Amount: (Pp) Personal participation rate - Baseline rent (part of Tl)
- **Comp_Cond** = 5 variants
- **Comp_perTU** = 5 variants
- **Output_Var** = i_bho_rentbase
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / ArithOp
- Benefit Amount: (Pp) Personal participation rate - Rl= L  / Rent Baseline
- **Formula** = i_bho_l/i_bho_rentbase
- **Output_Var** = i_bho_rl
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / BenCalc
- Benefit Amount: (Pp) Personal participation rate - rate
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **Output_Var** = i_bho_rate
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / BenCalc
- Benefit Amount: (Pp) Personal participation rate - Rate Min
- **Comp_Cond** = 3 variants
- **Comp_perTU** = 3 variants
- **Output_Var** = i_bho_minrate
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / ArithOp
- Benefit Amount: (Pp) Personal participation rate - Tp = Tf + Tl; Tl= Rate*RL – Rate Min
- **Formula** = i_bho_tf+ (i_bho_rate*i_bho_rl-i_bho_minrate)
- **Output_Var** = i_bho_tp
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / BenCalc
- Benefit Amount: (Pp) Personal participation rate - R0
- **Comp_Cond** = 5 variants
- **Comp_perTU** = 5 variants
- **Output_Var** = i_bho_r0
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / ArithOp
- Benefit Amount: (Pp) Personal participation rate - P0 = [8.5%*(L+C)]
- **Formula** = 0.085*(i_bho_l+i_bho_c)
- **LowLim** = $bho_p0
- **Output_Var** = i_bho_p0
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / ArithOp
- Benefit Amount: (Pp) Personal participation rate - Pp=P0 + Tp * Rp (Rp=Global gross revenue-R0)
- **Formula** = i_bho_p0+i_bho_tp*max(il_rgby#1-i_bho_r0,0)
- **#_LowLim** = 0
- **Output_Var** = i_bho_pp
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / Elig
- BEN: Housing Benefits (Allocation Logement APL and AL)
- **Elig_Cond** = xhcrt>0
- **TAX_UNIT** = tu_bho_fr

## bhotn_fr / ArithOp
- Benefit Amount: Final benefit entitlement
- **Who_Must_Be_Elig** = all
- **Formula** = i_bho_l+i_bho_c-i_bho_pp
- **LowLim** = 0
- **Output_Var** = bhotn_s
- **TAX_UNIT** = tu_bho_fr
- **Threshold** = 15#m

## bhotn_fr / DefConst
- BEN: Housing Benefits (Allocation Logement APL and AL)
- **$bho_l_lt1** = 292.62#m
- **$bho_l_lt2** = 255.03#m
- **$bho_l_lt3** = 239.02#m
- **$bho_l_lt4** = 352.92#m
- **$bho_l_lt5** = 312.15#m
- **$bho_l_lt6** = 289.76#m
- **$bho_l_lt7** = 398.87#m
- **$bho_l_lt8** = 351.25#m
- **$bho_l_lt9** = 324.89#m
- **$bho_l_lt10** = 456.73#m
- **$bho_c3** = 12.06#m
- **$bho_c2** = 65.29#m
- **$bho_c1** = 53.23#m
- **$bho_l_lt15** = 46.56#m
- **$bho_l_lt14** = 51.12#m
- **$bho_l_lt13** = 57.86#m
- **$bho_l_lt12** = 371.45#m
- **$bho_l_lt11** = 402.37#m
- **$bho_rentbase3** = 351.25#m
- **$bho_rentbase2** = 312.15#m
- **$bho_rentbase1** = 255.03#m
- **$bho_tf8** = -0.0006
- **$bho_tf6** = 0.0185
- **$bho_tf5** = 0.0201
- **$bho_tf4** = 0.0238
- **$bho_tf3** = 0.027
- **$bho_tf2** = 0.0315
- **$bho_tf1** = 0.0283
- **$bho_r03** = 7762#y
- **$bho_r02** = 6508#y
- **$bho_r01** = 4544#y
- **$bho_rentbase5** = 51.12#m
- **$bho_rentbase4** = 402.37#m
- **$bho_r05** = 304#y
- **$bho_r04** = 7938#y
- **$bho_p0** = 34.73#m
- **$bho_tf7** = 0.0179
- **$bho_rl_rate1** = 0
- **$bho_rl_rate2** = 0.45
- **$bho_rl_rate3** = 0.68
- **$bho_rl_minrate1** = 0
- **$bho_rl_minrate2** = 0.2025
- **$bho_rl_minrate3** = 0.375

## bhotn_fr / BenCalc
- Since July 2016, if  the real rent paid is over a threshold, the benefit is suppressed
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bhotn_fr / BenCalc
- Since July 2016, if  the real rent paid is over a threshold, the benefit is suppressed
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bsaoa_fr / DefConst
- BEN: Solidarity allowance for the elderly (Allocation de solidarité aux personnes agées ASPA)
- **$bsaoa_amt1** = 800#m
- **$bsaoa_amt2** = 1242#m

## bsaoa_fr / BenCalc
- BEN: Solidarity allowance for the elderly (Allocation de solidarité aux personnes agées ASPA)
- **Comp_Cond** = 2 variants
- **#_level** = tu_individual_fr
- **Comp_perTU** = 2 variants
- **Withdraw_Base** = (max(il_rniy_bens,0)+bdi_s)
- **Withdraw_Rate** = 1
- **Output_Var** = bsaoa_s
- **TAX_UNIT** = tu_fiscalunit_fr

## bchlp_fr / DefConst
- Constants
- **$bchlp_fm01** = n/a
- **$bchlp_fm02** = n/a
- **$bchlp_fm03** = n/a
- **$bchlp_fm04** = n/a
- **$bchlp_hp01** = n/a
- **$bchlp_hp02** = n/a
- **$bchlp_hp03** = n/a

## bchlp_fr / DefVar
- Temporary variables
- **temp_bchlp_mininc** = n/a
- **temp_bchlp_dhp** = n/a

## bchlp_fr / BenCalc
- Eligibility: Calculate applicaple family minimum
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Comp_perElig** = n/a
- **#_N** = n/a
- **#_M** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bchlp_fr / BenCalc
- Amount: Calculate deductible housing package
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bchlp_fr / DefIl
- Income test: il_bchlp
- **il_rniy** = n/a
- **bdi_s** = n/a
- **bchlg_s** = n/a
- **bch00_s** = n/a
- **bchot_s** = n/a

## bchlp_fr / Elig
- Eligibility: child under 3
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## bchlp_fr / BenCalc
- Amount: Detemine final benefit entitlement
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Withdraw_Base** = n/a
- **Withdraw_Rate** = n/a
- **LowLim** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bsa00_fr / DefVar
- Define temporary variables
- **i_bsa00_amt** = 0
- **i_bsa00_ded** = 0
- **i_bsa00_bonus** = 0
- **i_bsa00_faminc** = 0
- **i_bsa00_wkinc** = 0

## bsa00_fr / DefIl
- Income test: il_bsa00
- **bdi_s** = +
- **bchlp_s** = n/a
- **bchlg_s** = +
- **bch00_s** = +
- **bchot_s** = +
- **bsaot** = +
- **bchcc_s** = +
- **bchor_s** = +
- **ils_earns** = +
- **ypt** = +
- **ypr** = +
- **yiy** = +
- **bhl** = +
- **bsuwd_s** = +
- **il_tscxc_pen** = +
- **bunmt_s** = +
- **bunct_s** = +
- **tscdf_s** = -
- **tscxc_s** = -
- **ils_sicse** = -
- **ils_sicee** = -
- **xmp** = -
- **tintcee_s** = +
- **bwkmcee_s** = n/a

## bsa00_fr / BenCalc
- Benefit Amount: Calculate maximum benefit based on household composition
- **Comp_Cond** = 10 variants
- **Comp_perTU** = 8 variants
- **#_AgeMax** = 2
- **#_AgeMin** = 0
- **#_N** = 3
- **#_M** = 99
- **Comp_perElig** = $bsa00_amt4
- **comp_cond** = nAdultsInTu=1 & IsNtoMchild#1 & nPersInUnit#2>0
- **comp_perElig** = $bsa00_amt10
- **Output_Var** = i_bsa00_amt
- **TAX_UNIT** = tu_bsa00_fr

## bsa00_fr / BenCalc
- Benefit Amount:Calculate applicable housing package to be deducted
- **Comp_Cond** = 5 variants
- **Comp_perTU** = 5 variants
- **Output_Var** = i_bsa00_ded
- **TAX_UNIT** = tu_bsa00_fr

## bsa00_fr / Elig
- BEN: Main means-tested social assistance benefit (Revenu minimum d’insertion RMI/Revenue de solidarité active  RSA )
- **Elig_Cond** = IsHeadOfTu & ( dag>=25 \\
- **TAX_UNIT** = tu_bsa00_fr

## bsa00_fr / BenCalc
- Benefit amount: Assign benefit amount to entitled families
- **Who_Must_Be_Elig** = one
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Withdraw_Base** = max(il_bsa00,0)
- **Withdraw_Rate** = 1
- **LowLim** = 0
- **Output_Var** = bsa00_s
- **TAX_UNIT** = tu_bsa00_fr

## bsa00_fr / BenCalc
- Benefit amount: Calculate end of year bonus
- **comp_cond** = 7 variants
- **comp_perTU** = 4 variants
- **#_N** = 3
- **#_M** = 99
- **comp_perElig** = $bsa00_bonus4
- **output_var** = i_bsa00_bonus
- **TAX_UNIT** = tu_bsa00_fr
- **Who_Must_Be_Elig** = one

## bsa00_fr / BenCalc
- Add end of year bonus to the main benefit
- **comp_cond** = bsa00_s>0
- **comp_perTU** = i_bsa00_bonus
- **output_add_var** = bsa00_s
- **TAX_UNIT** = tu_bsa00_fr

## bsa00_fr / BenCalc
- Adjust benefit in light of non-take-up
- **comp_cond** = 2 variants
- **comp_perTU** = bsa00_s
- **output_var** = bsa00_s
- **TAX_UNIT** = tu_individual_fr

## bsa00_fr / DefConst
- Parameters for RSA
- **$bsa00_amt1** = 513.88#m
- **$bsa00_amt2** = 770.82#m
- **$bsa00_amt3** = 924.98#m
- **$bsa00_amt4** = 205.55#m
- **$bsa00_amt5** = 770.82#m
- **$bsa00_amt6** = 924.98#m
- **$bsa00_amt10** = 219.96#m
- **$bsa00_amt9** = 1099.81#m
- **$bsa00_amt8** = 884.26#m
- **$bsa00_amt7** = 1079.15#m
- **$bsa00_bonus5** = 320.14#y
- **$bsa00_bonus4** = 60.98#y
- **$bsa00_bonus3** = 274.41#y
- **$bsa00_bonus2** = 228.67#y
- **$bsa00_bonus1** = 152.45#y
- **$bsa00_hp5** = 152.62#m
- **$bsa00_hp4** = 123.33#m
- **$bsa00_hp3** = 152.62#m
- **$bsa00_hp2** = 123.33#m
- **$bsa00_hp1** = 61.67#m

## bsa00_fr / Elig
- BEN: Main means-tested social assistance benefit (Revenu minimum d’insertion RMI/Revenue de solidarité active  RSA )
- **Elig_Cond** = i_takeup2>0.84
- **TAX_UNIT** = tu_individual_fr

## bsa00_fr / Elig
- Bonus given to families receiving in Dec  & November only- deactivated for HHoT data
- **Run_Cond** = IsUsedDatabase#1
- **#_DataBasename** = FR_*_hhot
- **Elig_Cond** = i_takeup2>=0
- **TAX_UNIT** = tu_individual_fr

## bsa00_fr / ArithOp
- Calculate family work income
- **formula** = (ils_earns + il_temp_bun + bhl) - (ils_sicee + ils_sicse) - (i_tscxc_earns + i_tscxc_unemp + i_tscxc_bhl) - $tscdf_rate * ((1 - $csg_red) * (ils_earns + il_temp_bun) + bhl)
- **lowlim** = 0
- **output_var** = i_bsa00_wkinc
- **TAX_UNIT** = tu_individual_fr

## tscdf_fr / DefIl
- Base taxed with a reduction
- **ils_earns_csg** = +
- **bunct_s** = +

## tscdf_fr / ArithOp
- Liability
- **Formula** = il_crds_base_full * $tscdf_rate + il_crds_base_red * (1 - $csg_red) * $tscdf_rate
- **Output_Var** = tscdf_s
- **TAX_UNIT** = tu_individual_fr
- **LowLim** = 0

## tscdf_fr / DefConst
- Policy parameters
- **$tscdf_rate** = 0.005

## tscdf_fr / DefIl
- Base fully taxed
- **il_tscxc_pen** = +
- **il_capy** = +
- **bhl** = +
- **bch00_s** = +
- **bched_s** = +
- **bchlg_s** = +
- **bchyc_s** = +
- **bchba_s** = +
- **bhotn_s** = +
- **bhoot** = +
- **bchor_s** = +
- **bchcc_s** = +
- **bmact_s** = +
- **bpact_s** = +

## output_std_fr / DefOutput
- DEF: STANDARD OUTPUT INDIVIDUAL LEVEL
- **File** = FR_2015_std
- **vargroup** = 9 variants
- **ilgroup** = ils_*
- **TAX_UNIT** = tu_individual_fr
- **VarGroup** = 3 variants
- **ILGroup** = il_*
- **UnitInfo_TU** = 6 variants
- **UnitInfo_Id** = 2 variants
- **Var** = n/a

## output_std_hh_fr / DefOutput
- DEF: STANDARD OUTPUT HOUSEHOLD LEVEL
- **file** = FR_2015_std_hh
- **var** = 2 variants
- **ilgroup** = ils*
- **TAX_UNIT** = tu_household_fr

## SetDefault_fr / SetDefault
- Training data & hypo data defaults
- **Dataset** = 3 variants
- **bunct_s** = bun
- **pdi00** = pdi
- **yemmy** = 12
- **bunmt_s** = 0
- **ysemy** = 12
- **bsuwd_s** = bsuwd
- **yem00** = yem
- **poa00** = poa
- **drg01** = 1
- **ymwdt** = 0
- **bchot_s** = 0
- **bmact_s** = 0
- **bpact_s** = 0
- **liwmy_a** = 0
- **yempv_a** = 0
- **tmu** = 0
- **tin_s** = n/a

## SetDefault_fr / SetDefault
- General Default values
- **dataset** = FR_201?_a?
- **bsuwd_s** = bsuwd
- **bsaoa_s** = bsaoa
- **liwmy_s** = 0
- **Dataset** = 4 variants
- **poa00** = poa
- **tmu** = 0
- **twl** = tpr
- **bchcc** = 0
- **tin** = 0
- **tscer** = 0
- **yemxp** = 0
- **yem00** = yem
- **bchlp** = 0
- **yprrt** = ypr
- **kfbcc** = 0
- **bunmt_s** = bunmt
- **yptmp** = 0
- **tpr** = 0
- **bchba** = 0
- **bsawk** = 0
- **ymwdt** = 0
- **dmb** = 2
- **bmact_s** = 0
- **bpact_s** = 0
- **tscee** = 0
- **tscse** = 0
- **xed00** = 0
- **xhl00** = 0
- **kivho** = 0

## SetDefault_fr / SetDefault
- Defaults for LMA/RR
- **Dataset** = 10 variants
- **lhw_a** = 0
- **yem_a** = 0
- **yempv_a** = 0
- **liwmy_a** = 0
- **lnu** = 0
- **yem20_a** = 0
- **yem19_a** = 0
- **yem18_a** = 0
- **yemmy_a** = 0
- **lmc** = 0
- **lma** = 0
- **yemmy20_a** = 0
- **yemmy19_a** = 0
- **yemmy18_a** = 0
- **lhw20_a** = 0
- **lhw19_a** = 0
- **lhw18_a** = 0
- **lmc20** = 0
- **lma20** = 0
- **lma19** = 0
- **lma18** = 0
- **lowas** = 0

## SetDefault_fr / SetDefault
- DEF: Define defaults
- **Dataset** = 9 variants
- **yem01** = 0

## SetDefault_fr / ArithOp
- DEF: Define defaults
- **Formula** = poa+bsaoa
- **Output_Var** = poa
- **TAX_UNIT** = tu_individual_fr
- **Run_Cond** = IsUsedDatabase#1 \\
- **#_DataBasename** = 2 variants

## SetDefault_fr / ArithOp
- DEF: Define defaults
- **Formula** = 0
- **Output_Var** = tpr
- **TAX_UNIT** = tu_individual_fr
- **Run_Cond** = IsUsedDatabase#1 \\
- **#_DataBasename** = 2 variants

## SetDefault_fr / SetDefault
- DEF: Define defaults
- **Dataset** = fr_2007_*
- **ydses_o** = 0

## SetDefault_fr / DefConst
- Min Wage
- **$MinWage** = 1457.52#m
- **$Nwh** = 35
- **const_monetary** = no
- **$Minwage_hourly** = 9.61#m

## SetDefault_fr / InitVars
- Default values for Covid-19 monetary compensation schemes and social assistance
- **yemmc_s** = n/a
- **lhwsr_s** = n/a
- **bwkmceemy_s** = n/a
- **yemmwmy_s** = n/a
- **lhwsesr_s** = n/a
- **ysemwmy_s** = n/a
- **bwkmcsemy_s** = n/a
- **yemmw_s** = n/a
- **ysemw_s** = n/a

## bsawk_fr / DefVar
- BEN: Activity allowance (Prime d’activité)
- **i_bsawk_bonus** = n/a
- **i_bsawk_rt** = n/a
- **i_bsawk_nw** = n/a
- **i_bsawk_ded** = n/a
- **i_bsawk_amt** = n/a

## bsawk_fr / DefConst
- Parameters for activity allowance
- **$bsawk_minamt** = n/a
- **$bsawk_ratebonus** = n/a
- **$bsawk_rateinc** = n/a
- **$bsawk_hp1** = n/a
- **$bsawk_hp2** = n/a
- **$bsawk_hp3** = n/a
- **$bsawk_hp4** = n/a
- **$bsawk_hp5** = n/a
- **$bsawk_minamt1** = n/a
- **$bsawk_minamt2** = n/a
- **$bsawk_minamt3** = n/a
- **$bsawk_minamt4** = n/a
- **$bsawk_minamt5** = n/a
- **$bsawk_minamt6** = n/a

## bsawk_fr / BenCalc
- Calculate number of earners
- **Comp_Cond** = n/a
- **Comp_perElig** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a
- **#_Level** = n/a

## bsawk_fr / BenCalc
- Adjust benefit for non-take-up
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bsawk_fr / Elig
- Activity allowance bonus: Eligibility
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## bsawk_fr / ArithOp
- Calculate bonus in the activity allowance
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **LowLim** = n/a
- **UpLim** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bsawk_fr / BenCalc
- Activity allowance: Benefit amount
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a
- **Withdraw_Base** = n/a
- **Withdraw_Rate** = n/a
- **LowLim** = n/a
- **Threshold** = n/a

## bsawk_fr / BenCalc
- Benefit Amount:Calculate applicable housing package to be deducted
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bsawk_fr / BenCalc
- Benefit Amount: Calculate maximum benefit based on household composition
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **#_n** = n/a
- **#_m** = n/a
- **Comp_perElig** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## IlsDef_fr / DefIl
- ils_earns: Standardised Earnings
- **yse** = +
- **yem00** = +
- **yemxp** = +
- **yemmc_s** = n/a

## IlsDef_fr / DefIl
- ils_origy: Standardised Original income
- **ils_earns** = +
- **ypp** = +
- **yiy** = +
- **ypr** = +
- **yot** = +
- **ypt** = +
- **xmp** = -

## IlsDef_fr / DefIl
- ils_dispy: Standardised Disposable income
- **ils_origy** = +
- **ils_sicdy** = -
- **ils_tax** = -
- **ils_ben** = +

## IlsDef_fr / DefIl
- ils_tax: Standardised Taxes
- **tin_s** = +
- **tpr** = +
- **tscxc_s** = +
- **tscdf_s** = +
- **tsckt_s** = +
- **tinto_s** = +
- **tmu** = +
- **twl** = +

## IlsDef_fr / DefIl
- ils_benmt: Standardised Means-tested benefit-standardized
- **bchyc_s** = +
- **bsuwd_s** = +
- **bunmt_s** = +
- **bchlg_s** = +
- **bched_s** = +
- **bchba_s** = +
- **bsaoa_s** = +
- **bdi_s** = +
- **bchlp_s** = n/a
- **bsa00_s** = +
- **bhotn_s** = +
- **tinrf_s** = +
- **bchot_s** = +
- **bsaot** = +
- **bhoot** = +
- **bed** = +
- **bsawk_s** = n/a
- **bsaeccm_s** = n/a
- **binxp_s** = n/a
- **bhoey_s** = n/a
- **binpb_s** = n/a

## IlsDef_fr / DefIl
- ils_bennt: Standardised Non means-tested benefits
- **bhl** = +
- **bunct_s** = +
- **bch00_s** = +
- **bchcc_s** = +
- **bchor_s** = +
- **bmact_s** = +
- **bpact_s** = +
- **bwkmcee_s** = n/a
- **bwkmcse_s** = n/a
- **bseec_s** = n/a

## IlsDef_fr / DefIl
- ils_origrepy: Standardised Original & Replacement income
- **ils_origy** = +
- **ils_pen** = +
- **bunct_s** = +
- **bhl** = +
- **bwkmcee_s** = n/a
- **bwkmcse_s** = n/a
- **bseec_s** = n/a

## IlsDef_fr / DefIl
- ils_pen: Standardised Public Pensions
- **poa00** = +
- **pdi00** = +
- **psu** = +

## IlsDef_fr / DefIl
- ils_sicse: Standardised Self-employed Social Insurance contributions
- **tscsefa_s** = +
- **tscsesi_s** = +
- **tscsepi_s** = +
- **tscsedi_s** = +
- **tscseir_s** = +

## IlsDef_fr / DefIl
- ils_sicer: Standardised Employer Social insurance contributions
- **tscersi_s** = +
- **tscerfa_s** = +
- **tscerho_s** = +
- **tscerpi_s** = +
- **tscerot_s** = +
- **tscerui_s** = +
- **tscerir_s** = +
- **tscerrd_s** = -
- **tscerap_s** = +

## IlsDef_fr / DefIl
- ils_sicee: Standardised Employee Social insurance contributions
- **tsceesi_s** = +
- **tsceepi_s** = +
- **tsceeui_s** = +

## IlsDef_fr / DefIl
- ils_ben: standardized benefit list
- **ils_pen** = +
- **ils_benmt** = +
- **ils_bennt** = +

## IlsDef_fr / DefIl
- ils_taxsim: standardized simulated taxes
- **tin_s** = +
- **tscxc_s** = +
- **tscdf_s** = +
- **tsckt_s** = +
- **tinto_s** = +

## IlsDef_fr / DefIl
- ils_bensim: Standardized simulated benefits
- **bunct_s** = +
- **bunmt_s** = +
- **bdi_s** = +
- **bsuwd_s** = +
- **bch00_s** = +
- **bchba_s** = +
- **bchyc_s** = +
- **bchlg_s** = +
- **bched_s** = +
- **bchlp_s** = n/a
- **bsa00_s** = n/a
- **bsaoa_s** = +
- **bhotn_s** = +
- **tinrf_s** = +
- **bsawk_s** = n/a
- **bchor_s** = +
- **bchcc_s** = +
- **bwkmcee_s** = n/a
- **bwkmcse_s** = n/a
- **bsaeccm_s** = n/a
- **bseec_s** = n/a
- **bhoey_s** = n/a

## IlsDef_fr / DefIl
- Familiy benefits (ils_b1_bfa) - cleanup income list needed
- **bchot_s** = +
- **bchor_s** = +
- **bched_s** = +
- **bchlg_s** = +
- **bch00_s** = +
- **bchlp_s** = n/a
- **ils_b1_bcb** = +

## IlsDef_fr / DefIl
- Education benefits (ils_b1_bed)
- **bed** = +

## IlsDef_fr / DefIl
- Old-age benefits (ils_b1_boa)
- **bsaoa_s** = +
- **poa00** = +

## IlsDef_fr / DefIl
- Survivor benefits (ils_b1_bsu)
- **bsuwd_s** = +
- **psu** = +

## IlsDef_fr / DefIl
- Disability benefits (ils_b1_bdi)
- **bdi_s** = +
- **pdi00** = +

## IlsDef_fr / DefIl
- Unemployment benefits (ils_b1_bun)
- **bunmt_s** = +
- **bunct_s** = +
- **bwkmcee_s** = n/a
- **bwkmcse_s** = n/a
- **bseec_s** = n/a

## IlsDef_fr / DefIl
- Health/sickness benefits (ils_b1_bhl)
- **bhl** = +

## IlsDef_fr / DefIl
- Housing benefits (ils_b1_bho)
- **bhoot** = +
- **bhotn_s** = +
- **bhoey_s** = n/a

## IlsDef_fr / DefIl
- Social assistance (ils_b1_bsa)
- **bsawk_s** = n/a
- **bsaot** = +
- **bsa00_s** = +
- **tinrf_s** = +
- **bsaeccm_s** = n/a
- **binxp_s** = n/a
- **binpb_s** = n/a

## IlsDef_fr / DefIl
- Family and education benefits (ils_b2_bfaed)
- **ils_b1_bfa** = +
- **ils_b1_bed** = +

## IlsDef_fr / DefIl
- Pensions, disability and health benefits (ils_b2_penhl)
- **ils_b1_bhl** = +
- **ils_b1_bdi** = +
- **ils_b1_boa** = +
- **ils_b1_bsu** = +

## IlsDef_fr / DefIl
- Social assistance and housing benefits (ils_b2_bsaho)
- **ils_b1_bho** = +
- **ils_b1_bsa** = +

## IlsDef_fr / DefIl
- all social insurance contributions paid by (self-)employed and others
- **ils_sicee** = +
- **ils_sicot** = +
- **ils_sicse** = +

## IlsDef_fr / DefIl
- Income tax list used to calculate implicit tax rates
- **bsuwd_s** = +
- **ypr** = +
- **yiy** = +
- **yse** = +
- **ypp** = +
- **psu** = +
- **pdi00** = +
- **poa00** = +
- **bunmt_s** = +
- **bunct_s** = +
- **bhl** = +
- **yem00** = +
- **yemxp** = +
- **yemxp_s** = n/a

## IlsDef_fr / DefIl
- Exceptional high income tax list used to calculate implicit tax rates
- **bsuwd_s** = +
- **ypr** = +
- **yiy** = +
- **yse** = +
- **ypp** = +
- **psu** = +
- **pdi00** = +
- **poa00** = +
- **bunmt_s** = +
- **bunct_s** = +
- **bhl** = +
- **yem00** = +
- **yemxp** = +
- **yemxp_s** = n/a

## IlsDef_fr / DefIl
- Childbirth related benefits B1
- **bmact_s** = +
- **bpact_s** = +
- **bchba_s** = +
- **bchcc_s** = +
- **bchyc_s** = +

## IlsDef_fr / DefIl
- CDG tax list used to calcualte implicit tax rates
- **bhl** = +
- **bmact_s** = +
- **bpact_s** = +
- **bunct_s** = +
- **bwkmcee_s** = n/a
- **pdi00** = +
- **poa00** = +
- **psu** = +
- **yem00** = +
- **yemmc_s** = n/a
- **yemxp** = +
- **yiy** = +
- **ypp** = +
- **ypr** = +
- **yse** = +

## IlsDef_fr / DefIl
- CRDS tax list used to calculate implicit tax rates
- **bch00_s** = +
- **bchba_s** = +
- **bchcc_s** = +
- **bched_s** = +
- **bchlg_s** = +
- **bchor_s** = +
- **bchyc_s** = +
- **bhl** = +
- **bhoot** = +
- **bhotn_s** = +
- **bmact_s** = +
- **bpact_s** = +
- **bunct_s** = +
- **bwkmcee_s** = n/a
- **pdi00** = +
- **poa00** = +
- **psu** = +
- **yem00** = +
- **yemmc_s** = n/a
- **yemxp** = +
- **yiy** = +
- **ypp** = +
- **ypr** = +
- **yse** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of disposable income
- **ils_udb_ypt** = +
- **ils_udb_ypr** = +
- **ils_udb_ypp** = +
- **ils_udb_yiy** = +
- **ils_udb_yse** = +
- **ils_udb_yem** = +
- **ils_udb_bhl** = +
- **ils_udb_bun** = +
- **ils_udb_bdi** = +
- **ils_udb_bsu** = +
- **ils_udb_boa** = +
- **ils_udb_yot** = +
- **ils_udb_xmp** = -
- **ils_udb_bed** = +
- **ils_udb_bfa** = +
- **ils_udb_bho** = +
- **ils_udb_bsa** = +
- **ils_udb_tis** = -
- **ils_udb_tpr** = -
- **ils_udb_kfbcc** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition-company car
- **kfbcc** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of taxes and contributions
- **tsckt_s** = +
- **tscdf_s** = +
- **tscxc_s** = +
- **tin_s** = +
- **tsceeui_s** = +
- **tsceepi_s** = +
- **tsceesi_s** = +
- **tinto_s** = +
- **tscseir_s** = +
- **tscsedi_s** = +
- **tscsepi_s** = +
- **tscsesi_s** = +
- **tscsefa_s** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of wealth taxes
- **twl** = +
- **tpr** = +
- **tmu** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of maintenance payments
- **xmp** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of income of children under 16
- **yot** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of household transfers received
- **ypt** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of investment income
- **yiy** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of property income
- **ypr** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of private pensions
- **ypp** = +

## ilsudbdef_fr / DefIl
- Standardized SILc definition of self-employment income
- **yse** = +

## ilsudbdef_fr / DefIl
- Standardized SILc definition of employment income
- **yemxp** = +
- **yem00** = +
- **yemmc_s** = n/a

## ilsudbdef_fr / DefIl
- Standardized SILC definition for housing benefits
- **bhoot** = +
- **bhotn_s** = +
- **bhoey_s** = n/a

## ilsudbdef_fr / DefIl
- Standardized SILC definition of family benefits
- **bchor_s** = +
- **bched_s** = +
- **bchlg_s** = +
- **bchyc_s** = +
- **bch00_s** = +
- **bchot_s** = +
- **bchcc_s** = +
- **bchba_s** = +
- **bmact_s** = +
- **bpact_s** = +
- **bchlp_s** = n/a

## ilsudbdef_fr / DefIl
- Standardized SILC definition of social assistance/exclusion benefits
- **bsaot** = +
- **bsa00_s** = +
- **bsawk_s** = n/a
- **bsaeccm_s** = n/a
- **binxp_s** = n/a
- **binpb_s** = n/a
- **tinrf_s** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of education benefits
- **bed** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of sickness benefits
- **bhl** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of unemployment benefits
- **bunmt_s** = +
- **bunct_s** = +
- **bwkmcee_s** = n/a
- **bwkmcse_s** = n/a
- **bseec_s** = n/a

## ilsudbdef_fr / DefIl
- Standardized SILC definition of disability benefits
- **bdi_s** = +
- **pdi00** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definition of survivor benefits
- **psu** = +
- **bsuwd_s** = +

## ilsudbdef_fr / DefIl
- Standardized SILC definiton of old-age pensions
- **bsaoa_s** = +
- **poa00** = +

## bmact_fr / Elig
- BEN: Maternity leave (indemnités journalières de maternité)
- **Elig_Cond** = dgn = 0 & IsParentOfDepChild#1
- **TAX_UNIT** = tu_individual_fr
- **#_Level** = tu_bmact_fr
- **Output_Var** = i_elparent_bmact

## bmact_fr / BenCalc
- eligibility: previous insurance record based on observed values
- **Comp_Cond** = i_elparent_bmact=1 & yem00 > 0 & (yem00 >=(6/12*(169*$Minwage_hourly)) \\
- **Comp_perTU** = 1
- **Output_Var** = i_elparent_bmact
- **TAX_UNIT** = tu_individual_fr

## bmact_fr / Elig
- duration: define eligible child
- **Elig_Cond** = IsDepChild#1
- **TAX_UNIT** = tu_individual_fr
- **#_Level** = tu_bmact_fr
- **Output_Var** = i_elchild_bmact

## bmact_fr / ArithOp
- count the number of eligible children in TU
- **Formula** = nDepChildrenInTu#1
- **Output_Var** = i_nelchildren_bmact
- **TAX_UNIT** = tu_individual_fr
- **#_Level** = tu_bmact_fr

## bmact_fr / BenCalc
- duration: age of eligible child
- **Comp_Cond** = i_elchild_bmact=1
- **Comp_perTU** = (12-dmb)*(30.5/7)
- **Output_Var** = i_ageweeks_bmact
- **TAX_UNIT** = tu_individual_fr

## bmact_fr / BenCalc
- duration: weeks per child
- **Comp_Cond** = 4 variants
- **Comp_perTU** = 4 variants
- **Output_Var** = i_durweeks_bmact
- **TAX_UNIT** = tu_individual_fr
- **Comp_UpLim** = 4 variants
- **Comp_LowLim** = 0
- **#_Level** = tu_bch_fr

## bmact_fr / BenCalc
- this fuction allocates duration to head of TU (=mother)
- **Comp_Cond** = i_nelchildren_bmact>0
- **Comp_perTU** = i_durweeks_bmact/i_nelchildren_bmact
- **Output_Var** = i_durweeks_bmact
- **TAX_UNIT** = tu_bmact_fr

## bmact_fr / DefVar
- define intermediate variables
- **i_elparent_bmact** = 0
- **Var_Monetary** = 2 variants
- **i_elchild_bmact** = 0
- **i_ageweeks_bmact** = 0
- **i_nelchildren_bmact** = 0
- **i_durweeks_bmact** = 0
- **i_yempv_bmact** = 0

## bmact_fr / DefTu
- TU for maternity allowance
- **Type** = SUBGROUP
- **Members** = Partner & OwnDepChild & LooseDepChild
- **PartnerCond** = Default
- **DepChildCond** = Default & dag <1
- **ExtHeadCond** = nDepChOfCouple > 0 & dgn = 0
- **StopIfNoHeadFound** = no

## bmact_fr / BenCalc
- amount: identification of previous income
- **Comp_Cond** = yem00 > 0
- **Comp_perTU** = yivwg*max($lhw*52/12,yem00)
- **Output_Var** = i_yempv_bmact
- **TAX_UNIT** = tu_individual_fr

## bmact_fr / BenCalc
- Daily amount per eligible parent
- **Comp_Cond** = i_elparent_bmact=1
- **Comp_perTU** = (0.5*i_yempv_bmact/30.5)
- **Output_Var** = bmact_s
- **TAX_UNIT** = tu_individual_fr
- **Comp_UpLim** = $bma_max
- **Comp_LowLim** = $bma_min/30.5

## bmact_fr / ArithOp
- Total amount per eligible parent: convert to monthly terms
- **Formula** = (bmact_s* ( i_durweeks_bmact*7))/12
- **Output_Var** = bmact_s
- **TAX_UNIT** = tu_individual_fr

## bmact_fr / ArithOp
- deduct from sickness benefits
- **Formula** = bhl - bmact_s
- **Output_Var** = bhl
- **TAX_UNIT** = tu_individual_fr
- **LowLim** = 0

## bmact_fr / DefConst
- BEN: Maternity leave (indemnités journalières de maternité)
- **$bma_min** = 281.65#m
- **$bma_max** = 82.33

## bpact_fr / ArithOp
- deduct from sickness benefits
- **Formula** = bhl - bpact_s
- **Output_Var** = bhl
- **TAX_UNIT** = tu_individual_fr
- **LowLim** = 0

## bpact_fr / DefTu
- TU for paternity allowance
- **Type** = SUBGROUP
- **Members** = Partner & OwnDepChild & LooseDepChild
- **PartnerCond** = Default
- **DepChildCond** = Default & dag <1
- **ExtHeadCond** = nDepChOfCouple > 0 & dgn = 1
- **StopIfNoHeadFound** = no

## bpact_fr / BenCalc
- eligibility: previous insurance record based on observed values
- **Comp_Cond** = i_elparent_bpact=1 & yem00 > 0 & (yem00 >=(6/12*(169*$Minwage_hourly)) \\
- **Comp_perTU** = 1
- **Output_Var** = i_elparent_bpact
- **TAX_UNIT** = tu_individual_fr

## bpact_fr / Elig
- BEN: Paternity leave (indemnités journalières de paternité)
- **Elig_Cond** = dgn = 1 & IsParentOfDepChild#1
- **TAX_UNIT** = tu_individual_fr
- **#_Level** = tu_bpact_fr
- **Output_Var** = i_elparent_bpact

## bpact_fr / BenCalc
- amount: identification of previous income
- **Comp_Cond** = yem00 > 0
- **Comp_perTU** = yivwg*max($lhw*52/12,yem00)
- **Output_Var** = i_yempv_bpact
- **TAX_UNIT** = tu_individual_fr

## bpact_fr / BenCalc
- Total amount per eligible parent
- **Comp_Cond** = 2 variants
- **Comp_perTU** = 2 variants
- **Output_Var** = bpact_s
- **TAX_UNIT** = tu_individual_fr
- **#_Level** = tu_bpact_fr

## bpact_fr / ArithOp
- Amount: convert to monthly terms
- **Formula** = bpact_s/12
- **Output_Var** = bpact_s
- **TAX_UNIT** = tu_individual_fr

## bpact_fr / DefVar
- define intermediate variables
- **i_elparent_bpact** = 0
- **Var_Monetary** = 2 variants
- **i_elchild_bpact** = 0
- **i_yempv_bpact** = 0

## bpact_fr / ArithOp
- Benefit amount (daily)
- **Formula** = 0.5*i_yempv_bpact/30.5
- **Output_Var** = bpact_s
- **TAX_UNIT** = tu_individual_fr
- **UpLim** = $bma_max
- **LowLim** = $bma_min/30.5

## yemcomp_fr / DefVar
- temporary variables
- **i_yem00_orig** = n/a
- **Var_Monetary** = n/a
- **i_yemxp_orig** = n/a
- **i_yemmy_orig** = n/a
- **i_bwkmcee_s** = n/a
- **i_yemmc_s** = n/a
- **i_diff** = n/a

## yemcomp_fr / Elig
- eligibility condition for the policy
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## yemcomp_fr / ArithOp
- "real" monthly salary when not in compensation scheme
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## yemcomp_fr / BenCalc
- "real" monthly benefit paid by the state while in compensation scheme
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **LowLim** = n/a
- **UpLim** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## yemcomp_fr / BenCalc
- "real" monthly benefit paid by the firm while in compensation scheme
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a
- **LowLim** = n/a

## yemcomp_fr / ArithOp
- average monthly benefit paid by the state while in compensation scheme
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## yemcomp_fr / ArithOp
- average monthly benefit paid by the firm while in compensation scheme
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## ysecomp_fr / DefVar
- temporary variables
- **i_yse_orig** = n/a
- **Var_Monetary** = n/a
- **i_ysemy_orig** = n/a

## ysecomp_fr / Elig
- eligibility condition for the policy
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## ysecomp_fr / ArithOp
- "real" monthly income when not in compensation scheme
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## ysecomp_fr / BenCalc
- one-off benefit paid by the state when in compensation scheme
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **UpLim** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bseec_fr / Elig
- Eligibility condition
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## bseec_fr / ArithOp
- Amount
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **UpLim** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bsaeccm_fr / DefConst
- Lump-sum values per TU and per child
- **$LS_TU** = n/a
- **$LS_child** = n/a

## bsaeccm_fr / BenCalc
- Benefit calculation
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / DefConst
- ESTAT data: unemployment,  pre-COVID input data
- **$er_dgn0_deh1_ee** = n/a
- **$er_dgn0_deh2_ee** = n/a
- **$er_dgn0_deh3_ee** = n/a
- **$er_dgn1_deh1_ee** = n/a
- **$er_dgn1_deh2_ee** = n/a
- **$er_dgn1_deh3_ee** = n/a
- **$ur_dgn0_deh1_ee** = n/a
- **$ur_dgn0_deh2_ee** = n/a
- **$ur_dgn0_deh3_ee** = n/a
- **$ur_dgn1_deh1_ee** = n/a
- **$ur_dgn1_deh2_ee** = n/a
- **$ur_dgn1_deh3_ee** = n/a
- **$er_dgn0_se** = n/a
- **$er_dgn1_se** = n/a
- **$er_yemmy2** = n/a
- **$er_yemmy5** = n/a
- **$er_yemmy8** = n/a
- **$ur_yemmy2** = n/a
- **$ur_yemmy5** = n/a
- **$ur_yemmy8** = n/a
- **Run_Cond** = n/a

## TransLMA_fr / Elig
- eligibility conditions - transition non-employed to employed
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- random allocation (based on ESTAT data) - transition non-employed to employed
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / Elig
- eligibility conditions - transition employed to unemployed for employees
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- random allocation (based on ESTAT data) - transition employed to unemployed for employees
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / Elig
- eligibility conditions - transition employed to unemployed for self-employed
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- random allocation (based on ESTAT data) - transition employed to unemployed for self-employed
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / Elig
- eligibility conditions - yem_a
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / ArithOp
- set yem_a
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / Elig
- eligibility conditions -  lhw_a
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / ArithOp
- set lhw_a / hours worked per week (based on external statistics and/or assumptions)
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- set yemmy_a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / DefConst
- ESTAT data: MC for employees,  pre-COVID input data
- **$sh_mcee_l1_dgn0** = n/a
- **$sh_mcee_l2_dgn0** = n/a
- **$sh_mcee_l3_dgn0** = n/a
- **$sh_mcee_l4_dgn0** = n/a
- **$sh_mcee_l5_dgn0** = n/a
- **$sh_mcee_l1_dgn1** = n/a
- **$sh_mcee_l2_dgn1** = n/a
- **$sh_mcee_l3_dgn1** = n/a
- **$sh_mcee_l4_dgn1** = n/a
- **$sh_mcee_l5_dgn1** = n/a
- **$sh_mceemy_1** = n/a
- **$sh_mceemy_2** = n/a
- **$sh_mceemy_3** = n/a
- **$sh_mceemy_4** = n/a
- **$sh_mceemy_5** = n/a
- **$sh_mceemy_6** = n/a
- **$sh_mceemy_7** = n/a
- **$sh_mceemy_8** = n/a
- **$sh_mceemy_9** = n/a
- **$sh_0hours_ee** = n/a
- **$sh_15hours_ee** = n/a
- **$sh_45hours_ee** = n/a
- **$sh_mceemy_10** = n/a
- **$sh_mceemy_11** = n/a
- **Run_Cond** = n/a

## TransLMA_fr / DefConst
- ESTAT data: MC for self-employed, pre-COVID input data
- **$sh_mcse_l1_dgn0** = n/a
- **$sh_mcse_l2_dgn0** = n/a
- **$sh_mcse_l3_dgn0** = n/a
- **$sh_mcse_l4_dgn0** = n/a
- **$sh_mcse_l5_dgn0** = n/a
- **$sh_mcse_l1_dgn1** = n/a
- **$sh_mcse_l2_dgn1** = n/a
- **$sh_mcse_l3_dgn1** = n/a
- **$sh_mcse_l4_dgn1** = n/a
- **$sh_mcse_l5_dgn1** = n/a
- **$sh_mcsemy_1** = n/a
- **$sh_mcsemy_2** = n/a
- **$sh_mcsemy_3** = n/a
- **$sh_mcsemy_4** = n/a
- **$sh_mcsemy_5** = n/a
- **$sh_mcsemy_6** = n/a
- **$sh_mcsemy_7** = n/a
- **$sh_mcsemy_8** = n/a
- **$sh_mcsemy_9** = n/a
- **$sh_0hours_se** = n/a
- **$sh_15hours_se** = n/a
- **$sh_45hours_se** = n/a
- **$sh_mcsemy_10** = n/a
- **$sh_mcsemy_11** = n/a
- **Run_Cond** = n/a

## TransLMA_fr / Elig
- MC_EE step 1: eligibility conditions
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- MC_EE  step 2: random allocation (based on ESTAT statistics)
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / Elig
- MC_EE selected in step 2 -> eligible for step 3
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- MC_EE step 3a: random allocation of months in MC (based on ESTAT statistics)
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / ArithOp
- MC_EE step 3b: months out of MC (based on step 3a)
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / Elig
- MC_EE selected in step 3 -> eligible for step 4
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- MC_EE step 4: share of hours worked in MC (based on ESTAT statistics)
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / Elig
- MC_SE step 1: eligibility conditions
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- MC SE step 2: random allocation (based on ESTAT statistics)
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / Elig
- MC_SE selected in step 2 -> eligible for step 3
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- MC_SE step 3a: random allocation of months in MC (based on ESTAT statistics)
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / ArithOp
- MC_SE step 3b: months out of MC (based on step 3a)
- **Who_Must_Be_Elig** = n/a
- **Formula** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / Elig
- MC_SE selected in step 3 -> eligible for step 4
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / BenCalc
- MC_SE step 4: share of hours worked in MC (based on ESTAT statistics)
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## TransLMA_fr / DefConst
- ESTAT data: unemployment,  post-COVID input data
- **$er_dgn0_deh1_ee** = n/a
- **$er_dgn0_deh2_ee** = n/a
- **$er_dgn0_deh3_ee** = n/a
- **$er_dgn1_deh1_ee** = n/a
- **$er_dgn1_deh2_ee** = n/a
- **$er_dgn1_deh3_ee** = n/a
- **$ur_dgn0_deh1_ee** = n/a
- **$ur_dgn0_deh2_ee** = n/a
- **$ur_dgn0_deh3_ee** = n/a
- **$ur_dgn1_deh1_ee** = n/a
- **$ur_dgn1_deh2_ee** = n/a
- **$ur_dgn1_deh3_ee** = n/a
- **$er_dgn0_se** = n/a
- **$er_dgn1_se** = n/a
- **$er_yemmy2** = n/a
- **$er_yemmy5** = n/a
- **$er_yemmy8** = n/a
- **$ur_yemmy2** = n/a
- **$ur_yemmy5** = n/a
- **$ur_yemmy8** = n/a
- **Run_Cond** = n/a

## TransLMA_fr / DefConst
- ESTAT data: MC for employees,  post-COVID input data
- **$sh_mcee_l1_dgn0** = n/a
- **$sh_mcee_l2_dgn0** = n/a
- **$sh_mcee_l3_dgn0** = n/a
- **$sh_mcee_l4_dgn0** = n/a
- **$sh_mcee_l5_dgn0** = n/a
- **$sh_mcee_l1_dgn1** = n/a
- **$sh_mcee_l2_dgn1** = n/a
- **$sh_mcee_l3_dgn1** = n/a
- **$sh_mcee_l4_dgn1** = n/a
- **$sh_mcee_l5_dgn1** = n/a
- **$sh_mceemy_1** = n/a
- **$sh_mceemy_2** = n/a
- **$sh_mceemy_3** = n/a
- **$sh_mceemy_4** = n/a
- **$sh_mceemy_5** = n/a
- **$sh_mceemy_6** = n/a
- **$sh_mceemy_7** = n/a
- **$sh_mceemy_8** = n/a
- **$sh_mceemy_9** = n/a
- **$sh_0hours_ee** = n/a
- **$sh_15hours_ee** = n/a
- **$sh_45hours_ee** = n/a
- **$sh_mceemy_10** = n/a
- **$sh_mceemy_11** = n/a
- **Run_Cond** = n/a

## TransLMA_fr / DefConst
- ESTAT data: MC for self-employed, post-COVID input data
- **$sh_mcse_l1_dgn0** = n/a
- **$sh_mcse_l2_dgn0** = n/a
- **$sh_mcse_l3_dgn0** = n/a
- **$sh_mcse_l4_dgn0** = n/a
- **$sh_mcse_l5_dgn0** = n/a
- **$sh_mcse_l1_dgn1** = n/a
- **$sh_mcse_l2_dgn1** = n/a
- **$sh_mcse_l3_dgn1** = n/a
- **$sh_mcse_l4_dgn1** = n/a
- **$sh_mcse_l5_dgn1** = n/a
- **$sh_mcsemy_1** = n/a
- **$sh_mcsemy_2** = n/a
- **$sh_mcsemy_3** = n/a
- **$sh_mcsemy_4** = n/a
- **$sh_mcsemy_5** = n/a
- **$sh_mcsemy_6** = n/a
- **$sh_mcsemy_7** = n/a
- **$sh_mcsemy_8** = n/a
- **$sh_mcsemy_9** = n/a
- **$sh_0hours_se** = n/a
- **$sh_15hours_se** = n/a
- **$sh_45hours_se** = n/a
- **$sh_mcsemy_10** = n/a
- **$sh_mcsemy_11** = n/a
- **Run_Cond** = n/a

## binxp_fr / BenCalc
- BEN: Inflation compensation (Indemnité inflation)
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## binxp_fr / DefVar
- Define temporary variables
- **i_binxp_hh** = n/a

## binxp_fr / Elig
- 2022 Exceptional inflation bonus
- **Elig_Cond** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## binxp_fr / BenCalc
- BEN: Inflation compensation (Indemnité inflation)
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Comp_perElig** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a

## bhoey_fr / DefVar
- BEN: Energy voucher
- **i_bhoey_cu** = n/a

## bhoey_fr / BenCalc
- Compute Consumption Unit
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bhoey_fr / Elig
- The access is granted if the household’s RFR by consumption unit is under 10700/10800 euros
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## bhoey_fr / BenCalc
- Benefit amount is based on the household composition and on the RFR. In 2021, an exceptional additional energy bonus of 100 euros is given to benefiaciaries
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## bhoey_fr / DefConst
- BEN: Energy voucher
- **$i_thrsh_max_rfr** = n/a

## yempb_fr / BenCalc
- INC: Increment on Civil servants salaries to tackle inflation 2022 & 2023
- **Comp_Cond** = n/a
- **Comp_perElig** = n/a
- **Output_Add_Var** = n/a
- **TAX_UNIT** = n/a

## binps_fr / DefConst
- BEN: Exceptional purchasing power premium for public servants
- **$binps_incl1** = n/a
- **$binps_incl2** = n/a
- **$binps_incl3** = n/a
- **$binps_incl4** = n/a
- **$binps_incl5** = n/a
- **$binps_incl6** = n/a
- **$binps_incl7** = n/a
- **$binps_amt1** = n/a
- **$binps_amt2** = n/a
- **$binps_amt3** = n/a
- **$binps_amt4** = n/a
- **$binps_amt5** = n/a
- **$binps_amt6** = n/a
- **$binps_amt7** = n/a

## binps_fr / BenCalc
- "Real" monthly wages
- **Comp_Cond** = n/a
- **Comp_perTU** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a

## binps_fr / Elig
- BEN: Exceptional purchasing power premium for public servants
- **Elig_Cond** = n/a
- **TAX_UNIT** = n/a

## binps_fr / BenCalc
- BEN: Exceptional purchasing power premium for public servants
- **Who_Must_Be_Elig** = n/a
- **Comp_Cond** = n/a
- **Comp_perElig** = n/a
- **Output_Var** = n/a
- **TAX_UNIT** = n/a