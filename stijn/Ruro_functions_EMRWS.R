## ----ff_filter_silc-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ff_filter_silc <- function(silc, filter_opt, tableoutput){
  #necessary to have mw_CPI_tab and w_max
  if (filter_opt == "wiles"){
    silc <- silc %>% mutate(
      f_option = "wiles",
      lma = ifelse(les %in% c(1,3,5,7) & dec == 0 & dag < 65 & dag > 16 & byr + pdi + poa + psu == 0, 1, 0))
    # 9:other and 10:family worker (only in 2017) not included 
  } 
  if (filter_opt == "woles"){
    silc <- silc %>% mutate(
      f_option = "woles",
      lma = ifelse(les != 2 & dec == 0 & dag < 65 & dag > 16 & byr + pdi + poa + psu == 0, 1, 0))
  }
  silc <- silc %>% group_by(idhh) %>% mutate(
    hhlma = sum(lma)
  ) %>% ungroup()
  
  silc_f <- silc %>% mutate(
    group = case_when(dgn == 1 & idpartner == 0 ~ "sm",
                      dgn == 0 & idpartner == 0 ~ "sf",
                      dgn == 1 & idpartner != 0 ~ "cm",
                      dgn == 0 & idpartner != 0 ~ "cf"),
    year = as.numeric(str_sub(ddt, -4)),
    cond_lma_les = ifelse((f_option == "wiles" & les %in% c(1,3,5,7))|
                            (f_option == "woles" & les != 2), 1, 0), 
    cond_lma_dec = ifelse(dec == 0, 1, 0), 
    cond_lma_dag = ifelse(dag < 65 & dag > 16, 1, 0),
    cond_lma_byr = ifelse(byr == 0, 1, 0),
    cond_lma_pdi = ifelse(pdi == 0, 1, 0), 
    cond_lma_poa = ifelse(poa == 0, 1, 0), 
    cond_lma_psu = ifelse(psu == 0, 1, 0),
    cond_lma = ifelse(lma == 1, 1, 0),
    cond_lhw = ifelse(lhw <= 70, 1, 0), 
    cond_yivwg = ifelse(yivwg >= mw_CPI_tab$minwage[match(year, mw_CPI_tab$incomeyear)]/(38*4.33) 
                        & yivwg < w_max, 1, 0), 
    cond_yse = ifelse(yse <= 100 * mw_CPI_tab$CPI[match(year, mw_CPI_tab$incomeyear)]/100, 1, 0),
    cond_s_hhlma = ifelse((group %in% c("sm", "sf") & hhlma == 1) | (group %in% c("cm", "cf")), 1, 0),
    cond_c_partnerlma = ifelse((group %in% c("cm", "cf") & silc$lma[match(idpartner, silc$idperson)] == 1)
                               | (group %in% c("sm", "sf")), 1, 0),
    cond_c_partnerdgn = ifelse((group %in% c("cm", "cf") & silc$dgn[match(idpartner, silc$idperson)] != dgn)
                               | (group %in% c("sm", "sf")), 1, 0),
    cond_c_hhlma = ifelse((group %in% c("cm", "cf") & hhlma == 2) | (group %in% c("sm", "sf")), 1, 0), 
    filter_in = (cond_lma_les * cond_lma_dec * cond_lma_dag * cond_lma_byr * cond_lma_pdi * cond_lma_poa * cond_lma_psu
                 * cond_lhw * cond_yivwg * cond_yse * cond_s_hhlma * cond_c_hhlma * cond_c_partnerlma * cond_c_partnerdgn)
  )
  silc_f <- silc_f %>% mutate(
    cond_c_partnerfilter = ifelse((group %in% c("cm", "cf") & silc_f$filter_in[match(idpartner, silc_f$idperson)] == 1)
                                  | (group %in% c("sm", "sf")), 1, 0),
    filter_in = filter_in * cond_c_partnerfilter
  )
  
  samp <- silc %>% filter(idhh %in% (silc_f %>% filter(filter_in == 1) %>% pull(idhh)))
  
  if (tableoutput){
    filtertable_obs <- silc_f %>% group_by(group) %>% summarise(
      nofilter = n(),
      filter_lma_les = sum(cond_lma_les),
      filter_lma_dec = sum(cond_lma_les*cond_lma_dec),
      filter_lma_dag = sum(cond_lma_les*cond_lma_dec*cond_lma_dag),
      filter_lma_byr = sum(cond_lma_les*cond_lma_dec*cond_lma_dag*cond_lma_byr), 
      filter_lma_pdi = sum(cond_lma_les*cond_lma_dec*cond_lma_dag*cond_lma_byr*cond_lma_pdi),
      filter_lma_poa = sum(cond_lma_les*cond_lma_dec*cond_lma_dag*cond_lma_byr*cond_lma_pdi*cond_lma_poa),
      filter_lma_psu = sum(cond_lma_les*cond_lma_dec*cond_lma_dag*cond_lma_byr*cond_lma_pdi*cond_lma_poa*cond_lma_psu), 
      filter_lma = sum(cond_lma), 
      filter_lhw = sum(cond_lma*cond_lhw),
      filter_yivwg = sum(cond_lma*cond_lhw*cond_yivwg),
      filter_yse = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse), 
      filter_s_hhlma = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma), 
      filter_c_partnerlma = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma*cond_c_partnerlma), 
      filter_c_partnerdgn = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma*cond_c_partnerlma*cond_c_partnerdgn),
      filter_c_hhlma = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma*cond_c_partnerlma*cond_c_partnerdgn*cond_c_hhlma),
      filter_c_partnerfilter = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma*cond_c_hhlma*cond_c_partnerlma*cond_c_partnerdgn*cond_c_partnerfilter)
    ) %>%
      pivot_longer(cols = -group, names_to = 'Filter') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(sm_obs = sm, sf_obs = sf, cm_obs = cm, cf_obs = cf)
    filtertable_dwt <- silc_f %>% group_by(group) %>% summarise(
      nofilter = n(),
      filter_lma_les = sum(cond_lma_les*dwt),
      filter_lma_dec = sum(cond_lma_les*cond_lma_dec*dwt),
      filter_lma_dag = sum(cond_lma_les*cond_lma_dec*cond_lma_dag*dwt),
      filter_lma_byr = sum(cond_lma_les*cond_lma_dec*cond_lma_dag*cond_lma_byr*dwt), 
      filter_lma_pdi = sum(cond_lma_les*cond_lma_dec*cond_lma_dag*cond_lma_byr*cond_lma_pdi*dwt),
      filter_lma_poa = sum(cond_lma_les*cond_lma_dec*cond_lma_dag*cond_lma_byr*cond_lma_pdi*cond_lma_poa*dwt),
      filter_lma_psu = sum(cond_lma_les*cond_lma_dec*cond_lma_dag*cond_lma_byr*cond_lma_pdi*cond_lma_poa*cond_lma_psu*dwt), 
      filter_lma = sum(cond_lma*dwt), 
      filter_lhw = sum(cond_lma*cond_lhw*dwt),
      filter_yivwg = sum(cond_lma*cond_lhw*cond_yivwg*dwt),
      filter_yse = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*dwt), 
      filter_s_hhlma = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma*dwt), 
      filter_c_partnerlma = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma*cond_c_hhlma*cond_c_partnerlma*dwt), 
      filter_c_partnerdgn = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma*cond_c_hhlma*cond_c_partnerlma*cond_c_partnerdgn*dwt),
      filter_c_hhlma = sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma*cond_c_hhlma*dwt),
      filter_c_partnerfilter =sum(cond_lma*cond_lhw*cond_yivwg*cond_yse*cond_s_hhlma*cond_c_hhlma*cond_c_partnerlma*cond_c_partnerdgn*cond_c_partnerfilter*dwt)
    ) %>%
      pivot_longer(cols = -group, names_to = 'Filter') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(sm_dwt = sm, sf_dwt = sf, cm_dwt = cm, cf_dwt = cf)
    
    filtertable <- full_join(filtertable_obs, filtertable_dwt, by = "Filter")
    write.csv2(filtertable, paste0(outputfolder, "/", filter_opt, "/filtertable", silc_f$year[1], ".csv"), row.names = F)
    
    lm_beforefilter <- silc_f %>% mutate(
      working = ifelse(lhw > 0, 1, 0), 
      working_pt1 = ifelse(lhw >= 18.5 & lhw <= 20.5, 1, 0), 
      working_pt2 = ifelse(lhw >= 29.5 & lhw <= 30.5, 1, 0), 
      working_ft = ifelse(lhw >= 37.5 & lhw <= 40.5, 1, 0)
    )
    lm_afterfilter <- lm_beforefilter %>% filter(idhh %in% (silc_f %>% filter(filter_in == 1) %>% pull(idhh)))
    wtab_bf_all_dwt <- lm_beforefilter %>% summarise(
      group = "all",
      n = sum(dwt),
      working = sum(working*dwt), 
      working_pt1 = sum(working_pt1*dwt), 
      working_pt2 = sum(working_pt2*dwt), 
      working_ft = sum(working_ft*dwt)
    ) %>%
      pivot_longer(cols = -group, names_to = 'lm') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(all_dwt = all)
    wtab_bf_all_obs <- lm_beforefilter %>% mutate(dwt = 1) %>% summarise(
      group = "all",
      n = sum(dwt),
      working = sum(working*dwt), 
      working_pt1 = sum(working_pt1*dwt), 
      working_pt2 = sum(working_pt2*dwt), 
      working_ft = sum(working_ft*dwt)
    ) %>%
      pivot_longer(cols = -group, names_to = 'lm') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(all_obs = all)
    wtab_bf_gr_dwt <- lm_beforefilter %>% group_by(group) %>% summarise(
      n = sum(dwt),
      working = sum(working*dwt), 
      working_pt1 = sum(working_pt1*dwt), 
      working_pt2 = sum(working_pt2*dwt), 
      working_ft = sum(working_ft*dwt)
    ) %>%
      pivot_longer(cols = -group, names_to = 'lm') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(sm_obs = sm, sf_obs = sf, cm_obs = cm, cf_obs = cf)
    wtab_bf_gr_obs <- lm_beforefilter %>% mutate(dwt = 1) %>% group_by(group) %>% summarise(
      n = sum(dwt),
      working = sum(working*dwt), 
      working_pt1 = sum(working_pt1*dwt), 
      working_pt2 = sum(working_pt2*dwt), 
      working_ft = sum(working_ft*dwt)
    ) %>%
      pivot_longer(cols = -group, names_to = 'lm') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(sm_obs = sm, sf_obs = sf, cm_obs = cm, cf_obs = cf)
    wtab_bf_obs <- left_join(wtab_bf_all_obs, wtab_bf_gr_obs, by = "lm")
    wtab_bf_dwt <- left_join(wtab_bf_all_dwt, wtab_bf_gr_dwt, by = "lm")
    wtab_bf <- left_join(wtab_bf_obs, wtab_bf_dwt, by = "lm")
    
    write.csv2(wtab_bf, paste0(outputfolder, "/", filter_opt, "/lm_beforefilter", silc_f$year[1], ".csv"), row.names = F)
    
    wtab_af_all_dwt <- lm_afterfilter %>% summarise(
      group = "all",
      n = sum(dwt),
      working = sum(working*dwt), 
      working_pt1 = sum(working_pt1*dwt), 
      working_pt2 = sum(working_pt2*dwt), 
      working_ft = sum(working_ft*dwt)
    ) %>%
      pivot_longer(cols = -group, names_to = 'lm') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(all_dwt = all)
    wtab_af_all_obs <- lm_afterfilter %>% mutate(dwt = 1) %>% summarise(
      group = "all",
      n = sum(dwt),
      working = sum(working*dwt), 
      working_pt1 = sum(working_pt1*dwt), 
      working_pt2 = sum(working_pt2*dwt), 
      working_ft = sum(working_ft*dwt)
    ) %>%
      pivot_longer(cols = -group, names_to = 'lm') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(all_obs = all)
    wtab_af_gr_dwt <- lm_afterfilter %>% group_by(group) %>% summarise(
      n = sum(dwt),
      working = sum(working*dwt), 
      working_pt1 = sum(working_pt1*dwt), 
      working_pt2 = sum(working_pt2*dwt), 
      working_ft = sum(working_ft*dwt)
    ) %>%
      pivot_longer(cols = -group, names_to = 'lm') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(sm_obs = sm, sf_obs = sf, cm_obs = cm, cf_obs = cf)
    wtab_af_gr_obs <- lm_afterfilter %>% mutate(dwt = 1) %>% group_by(group) %>% summarise(
      n = sum(dwt),
      working = sum(working*dwt), 
      working_pt1 = sum(working_pt1*dwt), 
      working_pt2 = sum(working_pt2*dwt), 
      working_ft = sum(working_ft*dwt)
    ) %>%
      pivot_longer(cols = -group, names_to = 'lm') %>% 
      pivot_wider(names_from = group, values_from = value) %>% 
      rename(sm_obs = sm, sf_obs = sf, cm_obs = cm, cf_obs = cf)
    wtab_af_obs <- left_join(wtab_af_all_obs, wtab_af_gr_obs, by = "lm")
    wtab_af_dwt <- left_join(wtab_af_all_dwt, wtab_af_gr_dwt, by = "lm")
    wtab_af <- left_join(wtab_af_obs, wtab_af_dwt, by = "lm")
    write.csv2(wtab_af, paste0(outputfolder, "/", filter_opt, "/lm_afterfilter", silc_f$year[1], ".csv"), row.names = F)
    
    lm_beforefilter2 <- lm_beforefilter %>% mutate(group = "all")
    lm_beforefilter_double <- rbind(lm_beforefilter, lm_beforefilter2)
    ytab_bf_dwt <- lm_beforefilter_double %>% group_by(group, working, working_pt1, working_pt2, working_ft) %>%
      summarise(
        mean_dwt = weighted.mean(yivwg, dwt),
        p10_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.1), 
        p25_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.25),
        p50_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.5),
        p75_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.25),
        p90_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.9)
      ) 
    ytab_bf_obs <- lm_beforefilter_double %>% mutate(dwt = 1) %>% 
      group_by(group, working, working_pt1, working_pt2, working_ft) %>%
      summarise(
        mean_obs = weighted.mean(yivwg, dwt),
        p10_obs = weighted_quantile(v=yivwg, w=dwt, p=0.1), 
        p25_obs = weighted_quantile(v=yivwg, w=dwt, p=0.25),
        p50_obs = weighted_quantile(v=yivwg, w=dwt, p=0.5),
        p75_obs = weighted_quantile(v=yivwg, w=dwt, p=0.25),
        p90_obs = weighted_quantile(v=yivwg, w=dwt, p=0.9)
      )
    ytab_bf <- left_join(ytab_bf_obs, ytab_bf_dwt, by = c("group", "working", "working_pt1", "working_pt2", "working_ft"))
    write.csv2(ytab_bf, paste0(outputfolder, "/", filter_opt, "/wage_beforefilter", silc_f$year[1], ".csv"), row.names = F)
    
    lm_afterfilter2 <- lm_afterfilter %>% mutate(group = "all")
    lm_afterfilter_double <- rbind(lm_afterfilter, lm_afterfilter2)
    ytab_af_dwt <- lm_afterfilter_double %>% group_by(group, working, working_pt1, working_pt2, working_ft) %>%
      summarise(
        mean_dwt = weighted.mean(yivwg, dwt),
        p10_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.1), 
        p25_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.25),
        p50_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.5),
        p75_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.25),
        p90_dwt = weighted_quantile(v=yivwg, w=dwt, p=0.9)
      ) 
    ytab_af_obs <- lm_afterfilter_double %>% mutate(dwt = 1) %>% 
      group_by(group, working, working_pt1, working_pt2, working_ft) %>%
      summarise(
        mean_obs = weighted.mean(yivwg, dwt),
        p10_obs = weighted_quantile(v=yivwg, w=dwt, p=0.1), 
        p25_obs = weighted_quantile(v=yivwg, w=dwt, p=0.25),
        p50_obs = weighted_quantile(v=yivwg, w=dwt, p=0.5),
        p75_obs = weighted_quantile(v=yivwg, w=dwt, p=0.25),
        p90_obs = weighted_quantile(v=yivwg, w=dwt, p=0.9)
      )
    ytab_af <- left_join(ytab_af_obs, ytab_af_dwt, by = c("group", "working", "working_pt1", "working_pt2", "working_ft"))
    write.csv2(ytab_af, paste0(outputfolder, "/", filter_opt, "/wage_afterfilter", silc_f$year[1], ".csv"), row.names = F)
    
  }
  return(samp)
}
## ----ff_newids------------------------------------------------------------------------------------------------------
ff_newids <- function(samp){
  #add new ids
  samp <- samp %>% group_by(idhh) %>% mutate(
    hh_size = n(),
    personal_rank = order(order(-lma, -dgn, -dag, decreasing = FALSE))
  ) %>% ungroup() %>% mutate(
    year = as.numeric(str_sub(ddt, -4)), 
    idhhorig = idhh, 
    idpersonorig = idperson, 
    idpartnerorig = idpartner, 
    idfatherorig = idfather, 
    idmotherorig = idmother, 
    hh_rank = rank(idhhorig, ties.method = "min"), 
    idhh = (((year - 2000) * 10^nchar(dim(samp)[1])) + rank(idhhorig, ties.method = "min"))*100,
    idperson = (idhh * 100) + personal_rank * 100 
  )
  samp <- samp %>% mutate(
    idpartner = ifelse(idpartnerorig == 0, 0, samp$idperson[match(idpartnerorig, samp$idpersonorig)]),
    idfather = ifelse(idfatherorig == 0, 0, samp$idperson[match(idfatherorig, samp$idpersonorig)]),
    idmother = ifelse(idmotherorig == 0, 0, samp$idperson[match(idmotherorig, samp$idpersonorig)])
  )
  idhh_sm <- samp %>% filter(lma == 1 & idpartner == 0 & dgn == 1) %>% pull(idhh)
  idhh_sf <- samp %>% filter(lma == 1 & idpartner == 0 & dgn == 0) %>% pull(idhh)
  idhh_cou <- samp %>% filter(lma == 1 & idpartner != 0) %>% pull(idhh)
  samp <- samp %>% mutate(
    groupchar = case_when(idhh %in% idhh_sm ~ "sm",
                          idhh %in% idhh_sf ~ "sf",
                          idhh %in% idhh_cou ~ "cou"), 
    group = case_when(idhh %in% idhh_sm ~ 1,
                      idhh %in% idhh_sf ~ 0, 
                      idhh %in% idhh_cou ~ 10),
    groupy = year * 100 + group
  )
  return(samp)
}

## ----ff_newvars-----------------------------------------------------------------------------------------------------
ff_newvars <- function(samp, gsurtab_long, mw_CPI_tab, wri, afterrun = T){
  #after join of EM_output and aux and if wri == TRUE with dpi in samp
  samp <- samp %>% group_by(idhh) %>% mutate(
    children = sum(dag <= 18 | (dag <= 25 & dec != 0)),
    D_children6 = ifelse(sum(dag<6) >= 1, 1, 0), 
    children0_3 = sum(dag <= 3),
    children4_6 = sum(dag > 3 & dag <= 6),
    children7_9 = sum(dag > 6 & dag <= 9),
    children4_12 = sum(dag > 4 & dag <= 12),
    children0_13 = sum(dag <= 13), 
    deppers = hh_size - hhlma, 
    depadults = hh_size - hhlma - children
  ) %>% ungroup() %>% mutate(
    regW = ifelse(drgn1 == 3, 1, 0), 
    regB = ifelse(drgn1 == 1, 1, 0), 
    educL = ifelse(deh %in% c(0,1,2), 1, 0), 
    educH = ifelse(deh == 5, 1, 0),
    pexp = pmax(0, case_when(deh %in% c(0,1,2) ~ dag - 15, 
                             deh %in% c(3,4) ~ dag - 19,
                             TRUE ~ dag - 23))/100,
    gsur_category_year = paste0(case_when(dgn == 0 ~ "f", 
                                          dgn == 1 ~ "m"), "_", 
                                case_when(dag <= 14 ~ "00_14", 
                                          dag <= 24 ~ "15_24", 
                                          dag <= 54 ~ "25_54", 
                                          dag <= 64 ~ "55_64", 
                                          TRUE ~ "65_00"), "_", 
                                case_when(deh %in% c(0,1,2) ~ "loweduc", 
                                          deh %in% c(3,4) ~ "mideduc", 
                                          deh == 5 ~ "higheduc"), "_", year),
    gsur = gsurtab_long$GSURate[match(gsur_category_year, gsurtab_long$category_year)],
    yd1 = ifelse(match(year, years) == 1, 1, 0),
    yd2 = ifelse(match(year, years) == 2, 1, 0),
    yd3 = ifelse(match(year, years) == 3, 1, 0),
    uprating = mw_CPI_tab$CPI[match(2019, mw_CPI_tab$incomeyear)]/mw_CPI_tab$CPI[match(year, mw_CPI_tab$incomeyear)],
    
  )
  if(afterrun){
    samp <- samp %>% mutate(
      wage = ifelse(lma == 1 & hours > 0, yivwg, 0),
      working = ifelse(hours > 0, 1, 0), 
      working_pt1 = ifelse(hours >= 18.5 & hours <= 20.5, 1, 0), 
      working_pt2 = ifelse(hours >= 29.5 & hours <= 30.5, 1, 0), 
      working_ft = ifelse(hours >= 37.5 & hours <= 40.5, 1, 0), 
      ils_dispy = pmax(1, ils_dispy) #no negative incomes allowed for translog utility
    ) %>% group_by(idhh) %>% mutate(
      eqincome = sum(ils_dispy)/(1 + 0.5*(hh_size - children0_13) + 0.3*children0_13)
    ) %>% ungroup()
    if (wri) {
      samp <- samp %>% mutate(
        ils_dispy_th = (ils_dispy/dpi)/1000
      )
    } else {
      samp <- samp %>% mutate(
        ils_dispy_th = (ils_dispy * uprating)/1000
      )
    }
    samp <- samp %>% group_by(idhh) %>% mutate(
      tscer_hh = sum(tscer_s),
      ils_tax_hh = sum(ils_tax),
      ils_ben_hh = sum(ils_ben), 
      ils_sicdy_hh = sum(ils_sicdy)
    ) %>% ungroup()
  }
  return(samp)
}



## ----f_choicesets_sim-----------------------------------------------------------------------------------------------
f_choicesets_sim <- function(wasp, inputfolder, data, outputfolder, param, wri, gsurtab_long, mw_CPI_tab, delta_ld = FALSE, elast_ld_l = 0, elast_ld_m = 0, elast_ld_h = 0, delta_ep = 0){  
  silc <- read.delim(paste0(inputfolder, data))
  names_silc <- names(silc)
  samp <- ff_filter_silc(silc, "woles", TRUE)
  samp <- ff_newids(samp)
  samp <- ff_newvars(samp, gsurtab_long, mw_CPI_tab, wri, afterrun = FALSE)
  
  year <- as.numeric(str_sub(samp$ddt[1], -4))
  
  set.seed(1)
  samp_rep <- samp %>% group_by(idhh) %>% slice(rep(seq_len(n()), sizecs)) %>% ungroup()
  samp_rep$draw <- rep(rep(c(0:(sizecs-1)), length(unique(samp$idhh))), rep(samp$hh_size[samp$personal_rank == 1], each = sizecs))
  
  samp_rep <- samp_rep %>% mutate(
    hours = ifelse(draw == 0 & lma == 1, lhw, 0), 
    wage = ifelse(draw == 0 & lma == 1 & hours > 0, yivwg, 0), 
    #wage = wage_nominal * mw_CPI_tab$HPI[match(2019, mw_CPI_tab$incomeyear)]/mw_CPI_tab$HPI[match(year, mw_CPI_tab$incomeyear)],
    idhh_true = idhh,
    idhh = idhh + draw, 
    idperson = idperson + draw, 
    idfather = ifelse(idfather == 0, 0, idfather + draw), 
    idmother = ifelse(idmother == 0, 0, idmother + draw), 
    idpartner = ifelse(idpartner == 0, 0, idpartner + draw)
  )
  samp_rep <- samp_rep %>% mutate(
    pi0_d = 0,
    hours_d = 0, 
    wage_d = 0
  )
  
  #non-observed opportunities
  gamma0_m <- 1/((70-2-1-3)+2*exp(param[52])+1*exp(param[53])+3*exp(param[54]))
  gamma0_f <- 1/((70-2-1-3)+2*exp(param[61])+1*exp(param[62])+3*exp(param[63]))
  
  #breaks in distribution 
  h1_m <- gamma0_m * 18.5
  h2_m <- gamma0_m * (20.5 - 18.5) * exp(param[52])
  h3_m <- gamma0_m * (29.5 - 20.5)
  h4_m <- gamma0_m * (30.5 - 29.5) * exp(param[53])
  h5_m <- gamma0_m * (37.5 - 30.5)
  h6_m <- gamma0_m * (40.5 - 37.5) * exp(param[54])
  h7_m <- gamma0_m * (70 - 40.5)
  h1_f <- gamma0_f * 18.5
  h2_f <- gamma0_f * (20.5 - 18.5) * exp(param[61])
  h3_f <- gamma0_f * (29.5 - 20.5)
  h4_f <- gamma0_f * (30.5 - 29.5) * exp(param[62])
  h5_f <- gamma0_f * (37.5 - 30.5)
  h6_f <- gamma0_f * (40.5 - 37.5) * exp(param[63])
  h7_f <- gamma0_f * (70 - 40.5)
  
  print("draw random hours value")
  samp_rep[samp_rep$lma==1 & samp_rep$draw!=0,]$hours_d <- runif(nrow(samp_rep[samp_rep$lma==1 & samp_rep$draw!=0,]),0,1)
  samp_rep[samp_rep$lma==1 & samp_rep$draw!=0,]$pi0_d <- runif(nrow(samp_rep[samp_rep$lma==1 & samp_rep$draw!=0,]),0,1) 
  
  samp_rep <- samp_rep %>% mutate(
    intens = ifelse(dgn == 1,
                    ifelse(lma == 1 & draw != 0, 
                           exp(param[51] - log(gamma0_m) + param[55]*gsur + param[56]*regW + param[57]*regB + param[58]*educL + param[59]*educH)
                           /(1+exp(param[51] - log(gamma0_m) + param[55]*gsur + param[56]*regW + param[57]*regB + param[58]*educL + param[59]*educH)),
                           0),
                    ifelse(lma == 1 & draw != 0, 
                           exp(param[60] - log(gamma0_f) + param[64]*gsur + param[65]*regW + param[66]*regB + param[67]*educL + param[68]*educH)
                           /(1+exp(param[60] - log(gamma0_f) + param[64]*gsur + param[65]*regW + param[66]*regB + param[67]*educL + param[68]*educH)),
                           0)
    ),
    hours = ifelse(dgn == 1,
                   case_when(lma != 1 | draw == 0 ~ hours, 
                             pi0_d <= 1-intens ~ 0, 
                             hours_d <= h1_m ~ hours_d/gamma0_m, 
                             hours_d <= h1_m + h2_m ~ (18.5 + (hours_d - h1_m)/(gamma0_m*exp(param[52]))),
                             hours_d <= h1_m + h2_m + h3_m ~ (20.5 + (hours_d - h1_m - h2_m)/gamma0_m),
                             hours_d <= h1_m + h2_m + h3_m + h4_m ~ (29.5 + (hours_d - h1_m - h2_m - h3_m)/(gamma0_m*exp(param[53]))),
                             hours_d <= h1_m + h2_m + h3_m + h4_m + h5_m ~ (30.5 + (hours_d - h1_m - h2_m - h3_m - h4_m)/gamma0_m),
                             hours_d <= h1_m + h2_m + h3_m + h4_m + h5_m + h6_m
                             ~ (37.5 + (hours_d - h1_m - h2_m - h3_m - h4_m - h5_m)/(gamma0_m*exp(param[54]))),
                             hours_d <= h1_m + h2_m + h3_m + h4_m + h5_m + h6_m + h7_m
                             ~ (40.5 + (hours_d - h1_m - h2_m - h3_m - h4_m - h5_m - h6_m)/gamma0_m)),
                   case_when(lma != 1 | draw == 0 ~ hours, 
                             pi0_d <= 1-intens ~ 0, 
                             hours_d <= h1_f ~ hours_d/gamma0_f, 
                             hours_d <= h1_f + h2_f ~ (18.5 + (hours_d - h1_f)/(gamma0_f*exp(param[61]))),
                             hours_d <= h1_f + h2_f + h3_f ~ (20.5 + (hours_d - h1_f - h2_f)/gamma0_f),
                             hours_d <= h1_f + h2_f + h3_f + h4_f ~ (29.5 + (hours_d - h1_f - h2_f - h3_f)/(gamma0_f*exp(param[62]))),
                             hours_d <= h1_f + h2_f + h3_f + h4_f + h5_f ~ (30.5 + (hours_d - h1_f - h2_f - h3_f - h4_f)/gamma0_f),
                             hours_d <= h1_f + h2_f + h3_f + h4_f + h5_f + h6_f
                             ~ (37.5 + (hours_d - h1_f - h2_f - h3_f - h4_f - h5_f)/(gamma0_f*exp(param[63]))),
                             hours_d <= h1_f + h2_f + h3_f + h4_f + h5_f + h6_f + h7_f
                             ~ (40.5 + (hours_d - h1_f - h2_f - h3_f - h4_f - h5_f - h6_m)/gamma0_f))
    )
  )
  if (wasp == "fw"){
    samp_rep <- samp_rep %>% mutate(
      wage = ifelse(lma == 1 & draw != 0 & hours != 0, yivwg, wage),
      #wage = wage_nominal * mw_CPI_tab$HPI[match(2019, mw_CPI_tab$incomeyear)]/mw_CPI_tab$HPI[match(year, mw_CPI_tab$incomeyear)],
    )
  }
  if (wasp == "vw"){
    print("draw random value for wage distribution")
    samp_rep[samp_rep$lma==1 & samp_rep$draw!= 0 & samp_rep$hours>0,]$wage_d <- rnorm(nrow(samp_rep[samp_rep$lma==1 & samp_rep$draw!=0 & samp_rep$hours>0,]), 0,1)
    samp_rep <- samp_rep %>% mutate(
      lw = ifelse(dgn == 1,
                  param[69] + param[70]*educL + param[71]*educH + param[72]*pexp + param[73]*pexp^2 + param[81]*yd1 + param[82]*yd2,
                  param[74] + param[75]*educL + param[76]*educH + param[77]*pexp + param[78]*pexp^2 + param[81]*yd1 + param[82]*yd2),
      sdw = ifelse(dgn == 1, param[79], param[80]),
      wage = ifelse(lma != 1| draw == 0 | hours == 0, wage, exp(lw+(wage_d*sdw))), ##was before exp((wage_d+lw)*sdw)
      #wage_nominal = wage * mw_CPI_tab$HPI[match(year, mw_CPI_tab$incomeyear)]/mw_CPI_tab$HPI[match(2019, mw_CPI_tab$incomeyear)]
    )
  }
  
  if (delta_ld){
    samp_rep_delta_ld <- samp_rep %>% mutate(delta_ld_d = 0)
    samp_rep_delta_ld[samp_rep_delta_ld$lma==1,]$delta_ld_d <- runif(nrow(samp_rep_delta_ld[samp_rep_delta_ld$lma==1,]),0,1)
    samp_rep_delta_ld <- samp_rep_delta_ld %>% mutate(
      change_opp = case_when(educL == 1 ~ -(elast_ld_l*delta_ep),
                             educH == 1 ~ -(elast_ld_h*delta_ep), 
                             TRUE ~ -(elast_ld_m*delta_ep)),
      
      change_to_zero = ifelse(lma == 1 & hours > 0 & delta_ld_d <= change_opp, 1, 0),
      hours = ifelse(change_to_zero == 1, 0, hours), 
      wage = ifelse(change_to_zero == 1, 0, wage)
    )
    print(paste0("change in opportunities for low-educated: ", elast_ld_l*delta_ep*100, "%"))
    print(paste0("change in opportunities for mid-educated: ", elast_ld_m*delta_ep*100, "%"))
    print(paste0("change in opportunities for high-educated: ", elast_ld_h*delta_ep*100, "%"))
  }  
  
  samp_rep <- samp_rep %>% mutate(
    bun = ifelse(lma == 1 & hours > 0, 0, bun), 
    #reported bun is used only in cases of unemployment
    bsa = ifelse(lma == 1 & hours > 0, 0, bsa), 
    #reported bsa is used only in cases of unemployment
    yem = ifelse(lma == 1, hours * wage * 4.33, yem), 
    #yem is made consistent with chosen hours and wage
    lhw = hours, 
    #necessary as in EM lhw will be used (eg for calculation yemeq)
    yemmy = ifelse(lma != 1, yemmy, ifelse(hours > 0, 12, 0)),
    #assume in-work for 12 months (lma condition should not matter)
    lunmy = ifelse(lma != 1, lunmy, ifelse(hours > 0, 0, lunmy)),
    #assumption of no unemployment benefits should be consistent with lunmy
    yivwg = ifelse(lma != 1, yivwg, ifelse(hours > 0, wage, yivwg))
  )
  
  if (delta_ld){
    samp_rep_delta_ld <- samp_rep_delta_ld %>% mutate(
      bun = ifelse(lma == 1 & hours > 0, 0, bun), 
      #reported bun is used only in cases of unemployment
      bsa = ifelse(lma == 1 & hours > 0, 0, bsa), 
      #reported bsa is used only in cases of unemployment
      yem = ifelse(lma == 1, hours * wage * 4.33, yem), 
      #yem is made consistent with chosen hours and wage
      lhw = hours, 
      #necessary as in EM lhw will be used (eg for calculation yemeq)
      yemmy = ifelse(lma != 1, yemmy, ifelse(hours > 0, 12, 0)),
      #assume in-work for 12 months (lma condition should not matter)
      lunmy = ifelse(lma != 1, lunmy, ifelse(hours > 0, 0, lunmy)),
      #assumption of no unemployment benefits should be consistent with lunmy
      yivwg = ifelse(lma != 1, yivwg, ifelse(hours > 0, wage, yivwg))
    )
  }
  
  samp_EM_input_singles <- samp_rep %>% filter(group %in% c(0,1)) %>% select(all_of(names_silc)) %>% mutate_if(is.numeric, ~ round(., digits = 5))
  samp_EM_input_couples <- samp_rep %>% filter(group == 10) %>% select(all_of(names_silc)) %>% mutate_if(is.numeric, ~ round(., digits = 5))
  samp_aux <- samp_rep %>% select(idperson, all_of(setdiff(names(samp_rep), names_silc)))
  samp_EM_input_baseline <- samp_rep %>% filter(draw == 0) %>% select(all_of(names_silc)) %>% mutate_if(is.numeric, ~ round(., digits = 5))
  
  op_em_s <- paste0(inputfolder, "EM-SILC-choicesets/", 
                    "be_", year, ifelse(wri, "_wri", "_wai"), "_singles.txt")
  op_em_c <- paste0(inputfolder, "EM-SILC-choicesets/", 
                    "be_", year, ifelse(wri, "_wri", "_wai"), "_couples.txt")
  op_aux <-  paste0(inputfolder, "EM-SILC-choicesets/", 
                    "aux_", year, ifelse(wri, "_wri", "_wai"), "_sim.txt")
  op_em_b <- paste0(inputfolder, "EM-SILC/lma/",
                    "be_", year, "_z9.txt")
  
  print(paste0(op_em_b, " at ", Sys.time()))
  write.table(samp_EM_input_baseline, op_em_b, sep = "\t", row.names = FALSE, quote = FALSE)
  print(paste0(op_em_s, " at ", Sys.time()))
  write.table(samp_EM_input_singles, op_em_s, sep = "\t", row.names = FALSE, quote = FALSE)
  print(paste0(op_em_c, " at ", Sys.time()))
  write.table(samp_EM_input_couples, op_em_c, sep = "\t", row.names = FALSE, quote = FALSE)
  print(paste0(op_aux, " at ", Sys.time()))
  write.table(samp_aux, op_aux, sep = "\t", row.names = FALSE, quote = FALSE)
  
  if (delta_ld){
    samp_EM_input_singles_delta_ld <- samp_rep_delta_ld %>% filter(group %in% c(0,1)) %>% select(all_of(names_silc)) %>% mutate_if(is.numeric, ~ round(., digits = 5))
    samp_EM_input_couples_delta_ld <- samp_rep_delta_ld %>% filter(group == 10) %>% select(all_of(names_silc)) %>% mutate_if(is.numeric, ~ round(., digits = 5))
    samp_aux_delta_ld <- samp_rep_delta_ld %>% select(idperson, all_of(setdiff(names(samp_rep_delta_ld), names_silc)))
    
    op_em_s_dld <- paste0(inputfolder, "EM-SILC-choicesets/", 
                          "be_", year, ifelse(wri, "_wri", "_wai"), "_singles_dld.txt")
    op_em_c_dld <- paste0(inputfolder, "EM-SILC-choicesets/", 
                          "be_", year, ifelse(wri, "_wri", "_wai"), "_couples_dld.txt")
    op_aux_dld <- paste0(inputfolder, "EM-SILC-choicesets/",
                         "aux_", year, ifelse(wri, "_wri", "_wai"), "_sim_dld.txt")
    
    print(paste0(op_em_s_dld, " at ", Sys.time()))
    write.table(samp_EM_input_singles_delta_ld, op_em_s_dld, sep = "\t", row.names = FALSE, quote = FALSE)
    print(paste0(op_em_c_dld, " at ", Sys.time()))
    write.table(samp_EM_input_couples_delta_ld, op_em_c_dld, sep = "\t", row.names = FALSE, quote = FALSE)
    print(paste0(op_aux_dld, " at ", Sys.time()))
    write.table(samp_aux_delta_ld, op_aux_dld, sep = "\t", row.names = FALSE, quote = FALSE)
  }
}  

## ----f_preparedata_sim----------------------------------------------------------------------------------------------
f_preparedata_sim <- function(samp, wasp, gsurtab_long, mw_CPI_tab, wri){
  samp <- ff_newvars(samp, gsurtab_long, mw_CPI_tab, wri, afterrun = T)
  
  sm_p <- samp %>% filter(lma == 1 & group == 1)
  sf_p <- samp %>% filter(lma == 1 & group == 0)
  cou_p <- samp %>% filter(lma == 1 & group == 10) %>% mutate(dwt = round(dwt, digits = 4))
  #couples on one row
  common_variables <- c("idhh", "idhh_true", "idorighh", "group", "groupy", "dwt", 
                        "children0_3", "children4_6", "children7_9", 
                        "regW", "regB", "draw",
                        "yd1", "yd2", "yd3")
  cou_p <- cou_p %>%
    mutate(gender = ifelse(dgn == 1, "m", "f")) %>% 
    pivot_wider(id_cols = all_of(common_variables),
                names_from = gender,
                values_from = all_of(setdiff(colnames(cou_p), common_variables)))  
  
  out <- list("sm"=sm_p, "sf"=sf_p, "cou"=cou_p) 
  return(out)
}

## ----ff_read_price_evolution--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ff_read_price_evolution <- function(inputfolder, excel = "Indexen per productgroep vanaf 2006.xls", tab = "CPI-IPC 2013 = 100"){
  pricetable <- as.data.frame(read_xls(paste0(inputfolder, excel), sheet = tab)) %>% 
    filter(!str_detect(COICOP, "-")) %>% 
    rename_at(vars(18:220), ~ as.character(as.Date(as.numeric(.), origin = "1899-12-30"))) %>% 
    mutate(p_COICOP = paste0("p", str_remove_all(COICOP, "\\."))) %>% 
    reframe(p_COICOP = p_COICOP,
            y2015 = rowSums(across(starts_with("2015-")))/12,
            y2016 = rowSums(across(starts_with("2016-")))/12,
            y2017 = rowSums(across(starts_with("2017-")))/12,
            y2018 = rowSums(across(starts_with("2018-")))/12,
            y2019 = rowSums(across(starts_with("2019-")))/12,
            y2020 = rowSums(across(starts_with("2020-")))/12,
            y2021 = rowSums(across(starts_with("2021-")))/12) %>% 
    pivot_longer(starts_with("y"), names_to = "year", names_prefix = "y", values_to = "index")
}

## ----f_dpi_basey--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
f_dpi_basey <- function(df){
  df <- df %>% filter(hh_head==1)
  for (i in unique(str_sub(names(df)[startsWith(names(df), "xs")], start = 3, end = 7))){
    df <- df %>% mutate(
      dx = rowSums(across(starts_with(paste0("x", i)) & !contains("_na"))),
      dxx = rowSums(across(starts_with(paste0("xx", i)) & !contains("_na"))),
      dxs = rowSums(across(starts_with(paste0("xs", i)) & !contains("_na"))),
      dqi = ifelse(dx <= 0 | dxx <= 0, 1, dx/dxx),
      dqb = ifelse(dx <= 0 | dxx <= 0, NA, dx/dxx),
      dpi_tmp = dxs*log(dqi),
      dpi = dqi^dxs
    ) %>% rename_at(
      vars("dx", "dxx", "dxs", "dqi", "dqb", "dpi_tmp", "dpi"),
      ~ paste0(., i)
    )
  }
  df <- df %>% mutate(dpi = exp(rowSums(across(starts_with("dpi_tmp")))))
  return(df)  
}


## ----f_indirect_tax_rates-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
f_indirect_tax_rates <- function(df){
  df <- df %>% filter(hh_head == 1) %>% mutate(
    dx_tot = rowSums(across(starts_with("x0")|starts_with("x1") & !contains("_na"))),
    tva_tot = rowSums(across(starts_with("tva0")|starts_with("tva1") & !contains("_na"))),
    txv_tot = rowSums(across(starts_with("txv0")|starts_with("txv1") & !contains("_na"))),
    txa_tot = rowSums(across(starts_with("txa0")|starts_with("txa1") & !contains("_na"))),
    xdx = ifelse(dispy_hh <= 0, 0, dx_tot/dispy_hh),
    xtva = ifelse(dispy_hh <= 0, 0, tva_tot/dispy_hh),
    xtxv = ifelse(dispy_hh <= 0, 0, txv_tot/dispy_hh),
    xtxa = ifelse(dispy_hh <= 0, 0, txa_tot/dispy_hh)
  )
  return(df)
}

## ----f_add_consvars-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
f_add_consvars <- function(em_ruro, em_base_cis, new_rates_not_used_in_dpi){
  em_ruro <- em_ruro %>% mutate(
    dx_cq = new_rates_not_used_in_dpi$dx_tot[match(idorighh, new_rates_not_used_in_dpi$idorighh)],
    tva_cq = new_rates_not_used_in_dpi$tva_tot[match(idorighh, new_rates_not_used_in_dpi$idorighh)],
    txv_cq = new_rates_not_used_in_dpi$txv_tot[match(idorighh, new_rates_not_used_in_dpi$idorighh)],
    txa_cq = new_rates_not_used_in_dpi$txa_tot[match(idorighh, new_rates_not_used_in_dpi$idorighh)],
    xdx_nr = new_rates_not_used_in_dpi$xdx[match(idorighh, new_rates_not_used_in_dpi$idorighh)],
    xtva_nr = new_rates_not_used_in_dpi$xtva[match(idorighh, new_rates_not_used_in_dpi$idorighh)],
    xtxv_nr = new_rates_not_used_in_dpi$xtxv[match(idorighh, new_rates_not_used_in_dpi$idorighh)],
    xtxa_nr = new_rates_not_used_in_dpi$xtxa[match(idorighh, new_rates_not_used_in_dpi$idorighh)],
    xdx_cis = em_base_cis$xdx[match(idorighh, em_base_cis$idorighh)],
    xtva_cis = em_base_cis$xtva[match(idorighh, em_base_cis$idorighh)],
    xtxv_cis = em_base_cis$xtxv[match(idorighh, em_base_cis$idorighh)],
    xtxa_cis = em_base_cis$xtxa[match(idorighh, em_base_cis$idorighh)],
    dpi = em_base_cis$dpi[match(idorighh, em_base_cis$idorighh)], 
  )
  em_ruro <- em_ruro %>% group_by(idhh) %>% mutate(
    dispy_hh = sum(ils_dispy),
    expend_cq_hh = dx_cq, 
    tva_cq_hh = tva_cq, 
    txv_cq_hh = txv_cq,
    txa_cq_hh = txa_cq,
    expend_nr_hh = xdx_nr * dispy_hh, 
    tva_nr_hh = xtva_nr * dispy_hh, 
    txv_nr_hh = xtxv_nr * dispy_hh, 
    txa_nr_hh = xtxa_nr * dispy_hh,
    expend_cis_hh = xdx_cis * dispy_hh, 
    tva_cis_hh = xtva_cis * dispy_hh, 
    txv_cis_hh = xtxv_cis * dispy_hh, 
    txa_cis_hh = xtxa_cis * dispy_hh
  ) %>% ungroup() %>% mutate(
    ind_t_cq_hh = tva_cq_hh + txv_cq_hh + txa_cq_hh,
    ind_t_nr_hh = tva_nr_hh + txv_nr_hh + txa_nr_hh,
    ind_t_cis_hh = tva_cis_hh + txv_cis_hh + txa_cis_hh
  )
  return(em_ruro)
}

## ----ff_calc_util---------------------------------------------------------------------------------------------------
ff_calc_util <- function(param, df, type){
  if (type == "sm"){
    df <- df %>% mutate(
      util = ((param[1] + param[2]*log(dag) + param[3]*log(dag)^2 + param[4]*children4_6 + param[5]*children7_9
               + param[6]*regW + param[7]*regB + param[8]*educL + param[9]*educH)
              * (((168 - hours)/168)^param[10]-1)/param[10]
              + param[11] * (ils_dispy_th^param[12]-1)/param[12])
    )
  }
  if (type == "sf"){
    df <- df %>% mutate(
      util = ((param[13] + param[14]*log(dag) + param[15]*log(dag)^2 + param[16]*children0_3 + param[17]*children4_6 + param[18]*children7_9
               + param[19]*regW + param[20]*regB + param[21]*educL + param[22]*educH)
              * (((168 - hours)/168)^param[23]-1)/param[23]
              + param[24] * (ils_dispy_th^param[25]-1)/param[25])
    )
  }
  if (type == "cou"){
    df <- df %>% mutate(
      util = (((param[26] + param[27]*log(dag_m) + param[28]*log(dag_m)^2 + param[29]*children0_3 + param[30]*children4_6 + param[31]*children7_9
                + param[32]*regW + param[33]*regB + param[34]*educL_m + param[35]*educH_m)
               * (((168 - hours_m)/168)^param[46]-1)/param[46])
              + ((param[36] + param[37]*log(dag_f) + param[38]*log(dag_f)^2 + param[39]*children0_3 + param[40]*children4_6 + param[41]*children7_9
                  + param[42]*regW + param[43]*regB + param[44]*educL_f + param[45]*educH_f)
                 * (((168 - hours_f)/168)^param[47]-1)/param[47])
              + param[48] * ((ils_dispy_th_m + ils_dispy_th_f)^param[49]-1)/param[49]
              + param[50] * ((((168 - hours_m)/168)^param[46]-1)/param[46]) * ((((168 - hours_f)/168)^param[47]-1)/param[47])),
    )
  }
  return(df)
}


## ----f_simul3--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

f_simul3 <- function(param, sm_b, sf_b, cou_b, sm_r1, sf_r1, cou_r1, sm_r2, sf_r2, cou_r2, sm_r3, sf_r3, cou_r3, draws){  
  sm_b <- ff_calc_util(param, sm_b, "sm")
  sm_r1 <- ff_calc_util(param, sm_r1, "sm")
  sm_r2 <- ff_calc_util(param, sm_r2, "sm")
  sm_r3 <- ff_calc_util(param, sm_r3, "sm")
  sf_b <- ff_calc_util(param, sf_b, "sf")
  sf_r1 <- ff_calc_util(param, sf_r1, "sf")
  sf_r2 <- ff_calc_util(param, sf_r2, "sf")
  sf_r3 <- ff_calc_util(param, sf_r3, "sf")
  cou_b <- ff_calc_util(param, cou_b, "cou")
  cou_r1 <- ff_calc_util(param, cou_r1, "cou")
  cou_r2 <- ff_calc_util(param, cou_r2, "cou")
  cou_r3 <- ff_calc_util(param, cou_r3, "cou")
  
  for (i in 1:draws){
    print(paste0("draw ", i))
    set.seed(i)
    sm <- ff_predchoice3(sm_b, sm_r1, sm_r2, sm_r3)
    sm_b <- sm$df_b %>% rename_at(vars("gumb_draw", "util_tot"), ~ paste0(., i))
    sm_r1 <- sm$df_r1 %>% rename_at(vars("gumb_draw", "util_tot", "pred_choice"), ~ paste0(., i))
    sm_r2 <- sm$df_r2 %>% rename_at(vars("gumb_draw", "util_tot", "pred_choice"), ~ paste0(., i))
    sm_r3 <- sm$df_r3 %>% rename_at(vars("gumb_draw", "util_tot", "pred_choice"), ~ paste0(., i))
    sf <- ff_predchoice3(sf_b, sf_r1, sf_r2, sf_r3)
    sf_b <- sf$df_b %>% rename_at(vars("gumb_draw", "util_tot"), ~ paste0(., i))
    sf_r1 <- sf$df_r1 %>% rename_at(vars("gumb_draw", "util_tot", "pred_choice"), ~ paste0(., i))
    sf_r2 <- sf$df_r2 %>% rename_at(vars("gumb_draw", "util_tot", "pred_choice"), ~ paste0(., i))
    sf_r3 <- sf$df_r3 %>% rename_at(vars("gumb_draw", "util_tot", "pred_choice"), ~ paste0(., i))
    cou <- ff_predchoice3(cou_b, cou_r1, cou_r2, cou_r3)
    cou_b <- cou$df_b %>% rename_at(vars("gumb_draw", "util_tot"), ~ paste0(., i))
    cou_r1 <- cou$df_r1 %>% rename_at(vars("gumb_draw", "util_tot", "pred_choice"), ~ paste0(., i))
    cou_r2 <- cou$df_r2 %>% rename_at(vars("gumb_draw", "util_tot", "pred_choice"), ~ paste0(., i))
    cou_r3 <- cou$df_r3 %>% rename_at(vars("gumb_draw", "util_tot", "pred_choice"), ~ paste0(., i))
  }
  if (draws > 1){
    sm_r1 <- sm_r1 %>% mutate(exp = rowSums(across(starts_with("pred_choice")))/draws)
    sm_r2 <- sm_r2 %>% mutate(exp = rowSums(across(starts_with("pred_choice")))/draws)
    sm_r3 <- sm_r3 %>% mutate(exp = rowSums(across(starts_with("pred_choice")))/draws)
    sf_r1 <- sf_r1 %>% mutate(exp = rowSums(across(starts_with("pred_choice")))/draws)
    sf_r2 <- sf_r2 %>% mutate(exp = rowSums(across(starts_with("pred_choice")))/draws)
    sf_r3 <- sf_r3 %>% mutate(exp = rowSums(across(starts_with("pred_choice")))/draws)
    cou_r1 <- cou_r1 %>% mutate(exp = rowSums(across(starts_with("pred_choice")))/draws)
    cou_r2 <- cou_r2 %>% mutate(exp = rowSums(across(starts_with("pred_choice")))/draws)
    cou_r3 <- cou_r3 %>% mutate(exp = rowSums(across(starts_with("pred_choice")))/draws)
  } else{
    sm_r1 <- sm_r1 %>% mutate(exp = pred_choice1)
    sm_r2 <- sm_r2 %>% mutate(exp = pred_choice1)
    sm_r3 <- sm_r3 %>% mutate(exp = pred_choice1)
    sf_r1 <- sf_r1 %>% mutate(exp = pred_choice1)
    sf_r2 <- sf_r2 %>% mutate(exp = pred_choice1)
    sf_r3 <- sf_r3 %>% mutate(exp = pred_choice1)
    cou_r1 <- cou_r1 %>% mutate(exp = pred_choice1)
    cou_r2 <- cou_r2 %>% mutate(exp = pred_choice1)
    cou_r3 <- cou_r3 %>% mutate(exp = pred_choice1)
  }
  return(list("sm_b"=sm_b, "sf_b"=sf_b, "cou_b"=cou_b, "sm_r1"=sm_r1, "sf_r1"=sf_r1, "cou_r1"=cou_r1, "sm_r2"=sm_r2, "sf_r2"=sf_r2, "cou_r2"=cou_r2, "sm_r3"=sm_r3, "sf_r3"=sf_r3, "cou_r3"=cou_r3))
} 

## ----ff_gumbel----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ff_gumbel_draw <- function(df, uncond = F){
  if (!uncond){
    df$r_unif <- runif(nrow(df))
    df <- df %>% group_by(idhh_true) %>% mutate(
      obs_prob = sum(ifelse(draw == 0, exp(util), 0))/sum(exp(util))
    ) %>% ungroup() %>% mutate(
      gumb_draw = ifelse(draw == 0, -log(log(r_unif)*-obs_prob), 0)
    ) %>% group_by(idhh_true) %>% mutate(
      obs_util_tot = sum(ifelse(draw == 0, util + gumb_draw, 0)),
    ) %>% ungroup() %>% mutate(
      gumb_draw = ifelse(draw != 0, -log(-log(r_unif*(exp(-exp(util-obs_util_tot))))), gumb_draw),
      util_tot = util + gumb_draw
    )
  } else {
    df$r_unif <- runif(nrow(df))
    df <- df %>% mutate(
      gumb_draw = -log(-log(r_unif)),
      util_tot = util + gumb_draw
    )
  }
  return(df)
}
## ----ff_predchoice3--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

ff_predchoice3 <- function(df_b, df_r1, df_r2, df_r3){
  df_b <- ff_gumbel_draw(df_b, uncond = FALSE)
  df_r1 <- df_r1 %>% mutate(
    gumb_draw = df_b$gumb_draw[match(idhh, df_b$idhh)],
    util_tot = util + gumb_draw
  )
  id_pc1 <- df_r1 %>% group_by(idhh_true) %>% slice(which.max(util_tot)) %>% pull(idhh)
  df_r1 <- df_r1 %>% mutate(pred_choice = ifelse(idhh %in% id_pc1, 1, 0))
  rm(id_pc1)
  df_r2 <- df_r2 %>% mutate(
    gumb_draw = df_b$gumb_draw[match(idhh, df_b$idhh)],
    util_tot = util + gumb_draw
  )
  id_pc2 <- df_r2 %>% group_by(idhh_true) %>% slice(which.max(util_tot)) %>% pull(idhh)
  df_r2 <- df_r2 %>% mutate(pred_choice = ifelse(idhh %in% id_pc2, 1, 0))
  rm(id_pc2)
  df_r3 <- df_r3 %>% mutate(
    gumb_draw = df_b$gumb_draw[match(idhh, df_b$idhh)], 
    util_tot = util + gumb_draw
  )
  id_pc3 <- df_r3 %>% group_by(idhh_true) %>% slice(which.max(util_tot)) %>% pull(idhh)
  df_r3 <- df_r3 %>% mutate(pred_choice = ifelse(idhh %in% id_pc3, 1, 0))
  rm(id_pc3)
  return(list("df_b"= df_b, "df_r1"= df_r1, "df_r2"=df_r2, "df_r3"=df_r3))
}
## ----f_em_merge3--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

f_em_merge3 <- function(em_r1, em_r2, em_r3, varlist_b, varlist_b_com, varlist_r, varlist_r_com){
  varlist_b_s <- paste0(c(varlist_b_com, varlist_b),".obs")
  varlist_b_c <- paste0(c(varlist_b_com, paste0(varlist_b, "_m"), paste0(varlist_b, "_f")), ".obs")
  varlist_r_s <- c(paste0(c(varlist_r_com, varlist_r), ".for"),paste0(c(varlist_r_com, varlist_r), ".exp"))
  varlist_r_c <- c(paste0(c(varlist_r_com, paste0(varlist_r, "_m"), paste0(varlist_r, "_f")), ".for"), paste0(c(varlist_r_com, paste0(varlist_r, "_m"), paste0(varlist_r, "_f")), ".exp"))
  
  for (i in c("sm", "sf", "coum", "couf")){
    print(i)
    if(i == "sm"){
      df1 = em_r1$sm
      df2 = em_r2$sm
      df3 = em_r3$sm
      varlist_b <- varlist_b_s
      varlist_r <- varlist_r_s
    } else if (i == "sf"){
      df1 = em_r1$sf
      df2 = em_r2$sf
      df3 = em_r3$sf
      varlist_b <- varlist_b_s
      varlist_r <- varlist_r_s
    } else if (i == "coum"|i == "couf"){
      df1 = em_r1$cou
      df2 = em_r2$cou
      df3 = em_r3$cou
      varlist_b <- varlist_b_c
      varlist_r <- varlist_r_c
    } 
    df_all <- left_join(df1 %>% select(idhh_true, all_of(varlist_b)), 
                        df1 %>% select(idhh_true, all_of(varlist_r)) %>% rename_at(vars(all_of(varlist_r)), ~ str_c(., "_r1")), by = "idhh_true")
    df_all <- left_join(df_all, df2 %>% select(idhh_true, all_of(varlist_r)) %>% rename_at(vars(all_of(varlist_r)), ~ str_c(., "_r2")), by = "idhh_true")
    df_all <- left_join(df_all, df3 %>% select(idhh_true, all_of(varlist_r)) %>% rename_at(vars(all_of(varlist_r)), ~ str_c(., "_r3")), by = "idhh_true")
    df_all <- df_all %>% mutate(group = i)
    if (i == "coum"){df_all <- df_all %>% select(-contains("_f")) %>% rename_at(vars(contains("_m")), ~ str_remove(., "_m"))}
    if (i == "couf"){df_all <- df_all %>% select(-contains("_m")) %>% rename_at(vars(contains("_f")), ~ str_remove(., "_f"))}
    if (i == "sm"){sm_all <- df_all} else if (i == "sf"){sf_all <- df_all} else if (i == "coum"){coum_all <- df_all}else if (i == "couf"){couf_all <- df_all}
  }
  em_all <- rbind(sm_all, sf_all, coum_all, couf_all)
  return(em_all)
}
## ----f_em_exp-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
f_em_exp <- function(sm_b, sf_b, cou_b, sm_r, sf_r, cou_r){
  #calculates expected outcome (adds ".exp" to variables names when it is the expected outcome over the draws)
  print("sm")
  sm_b_obs <- sm_b %>% filter(draw==0) %>% rename_at(vars(-all_of(c("idhh_true", "idorighh"))), ~ str_c(., ".obs"))
  sm_r_for <- sm_r %>% filter(draw==0) %>% rename_at(vars(-all_of(c("idhh_true", "idorighh"))), ~ str_c(., ".for"))
  sm_r_exp <- sm_r %>% 
    mutate(across(where(is.numeric) & !starts_with("id"), ~ . * exp)) %>% 
    group_by(idhh_true) %>% 
    summarise(across(where(is.numeric) & !starts_with("id"), sum, na.rm=T, .names = "{.col}.exp"))
  sm <- left_join(sm_b_obs, sm_r_for, by = c("idhh_true", "idorighh"))
  sm <- left_join(sm, sm_r_exp, by = c("idhh_true"))
  sm <- sm %>% ungroup()
  print("sf")
  sf_b_obs <- sf_b %>% filter(draw==0) %>% rename_at(vars(-all_of(c("idhh_true", "idorighh"))), ~ str_c(., ".obs"))
  sf_r_for <- sf_r %>% filter(draw==0) %>% rename_at(vars(-all_of(c("idhh_true", "idorighh"))), ~ str_c(., ".for"))
  sf_r_exp <- sf_r %>% 
    mutate(across(where(is.numeric) & !starts_with("id"), ~ . * exp)) %>% 
    group_by(idhh_true) %>% 
    summarise(across(where(is.numeric) & !starts_with("id"), sum, na.rm=T, .names = "{.col}.exp"))
  sf <- left_join(sf_b_obs, sf_r_for, by = c("idhh_true", "idorighh"))
  sf <- left_join(sf, sf_r_exp, by = c("idhh_true"))
  sf <- sf %>% ungroup()
  print("cou")
  cou_b_obs <- cou_b %>% filter(draw==0) %>% rename_at(vars(-all_of(c("idhh_true", "idorighh"))), ~ str_c(., ".obs"))
  cou_r_for <- cou_r %>% filter(draw==0) %>% rename_at(vars(-all_of(c("idhh_true", "idorighh"))), ~ str_c(., ".for"))
  cou_r_exp <- cou_r %>% 
    mutate(across(where(is.numeric) & !starts_with("id"), ~ . * exp)) %>% 
    group_by(idhh_true) %>% 
    summarise(across(where(is.numeric) & !starts_with("id"), sum, na.rm = T, .names = "{.col}.exp"))
  cou <- left_join(cou_b_obs, cou_r_for, by = c("idhh_true", "idorighh"))
  cou <- left_join(cou, cou_r_exp, by = c("idhh_true"))
  cou <- cou %>% ungroup()
  
  out <- list("sm" = sm, "sf" = sf, "cou" = cou)
  return(out)
}

## ----f_aggregate_expenditure----------------------------------------------------------------------------------------
f_aggregate_expenditure <- function(em_data){
  #aggregate expenditure
  em_data <- em_data %>% mutate(
    dx01 = rowSums(across(starts_with("x01") & !contains("_na"))),
    dx02 = rowSums(across(starts_with("x02") & !contains("_na"))),
    dx03 = rowSums(across(starts_with("x03") & !contains("_na"))),
    dx04 = rowSums(across(starts_with("x04") & !contains("_na"))),
    dx05 = rowSums(across(starts_with("x05") & !contains("_na"))),
    dx06 = rowSums(across(starts_with("x06") & !contains("_na"))),
    dx07 = rowSums(across(starts_with("x07") & !contains("_na"))),
    dx08 = rowSums(across(starts_with("X08") & !contains("_na"))),
    dx09 = rowSums(across(starts_with("x09") & !contains("_na"))),
    dx10 = rowSums(across(starts_with("x10") & !contains("_na"))),
    dx11 = rowSums(across(starts_with("x11") & !contains("_na"))),
    dx12 = rowSums(across(starts_with("x12") & !contains("_na"))),
    dx_tot = rowSums(across(paste0("dx", c(paste0("0", 1:9), 10:12))))
  )  %>% mutate(
    dxx01 = rowSums(across(starts_with("xx01")  & !contains("_na"))), 
    dxx02 = rowSums(across(starts_with("xx02")  & !contains("_na"))),
    dxx03 = rowSums(across(starts_with("xx03")  & !contains("_na"))), 
    dxx04 = rowSums(across(starts_with("xx04")  & !contains("_na"))),
    dxx05 = rowSums(across(starts_with("xx05")  & !contains("_na"))),
    dxx06 = rowSums(across(starts_with("xx06")  & !contains("_na"))),
    dxx07 = rowSums(across(starts_with("xx07")  & !contains("_na"))),
    dxx08 = rowSums(across(starts_with("xx08")  & !contains("_na"))),
    dxx09 = rowSums(across(starts_with("xx09")  & !contains("_na"))),
    dxx10 = rowSums(across(starts_with("xx10")  & !contains("_na"))),
    dxx11 = rowSums(across(starts_with("xx11")  & !contains("_na"))),
    dxx12 = rowSums(across(starts_with("xx12")  & !contains("_na"))),
    dxx_tot = rowSums(across(paste0("dxx", c(paste0("0", 1:9), 10:12))))
  ) %>% mutate(
    tva01 = rowSums(across(starts_with("tva01")  & !contains("_na"))), 
    tva02 = rowSums(across(starts_with("tva02")  & !contains("_na"))),
    tva03 = rowSums(across(starts_with("tva03")  & !contains("_na"))), 
    tva04 = rowSums(across(starts_with("tva04")  & !contains("_na"))),
    tva05 = rowSums(across(starts_with("tva05")  & !contains("_na"))),
    tva06 = rowSums(across(starts_with("tva06")  & !contains("_na"))),
    tva07 = rowSums(across(starts_with("tva07")  & !contains("_na"))),
    tva08 = rowSums(across(starts_with("tva08")  & !contains("_na"))),
    tva09 = rowSums(across(starts_with("tva09")  & !contains("_na"))),
    tva10 = rowSums(across(starts_with("tva10")  & !contains("_na"))),
    tva11 = rowSums(across(starts_with("tva11")  & !contains("_na"))),
    tva12 = rowSums(across(starts_with("tva12")  & !contains("_na"))),
    tva_tot = rowSums(across(paste0("tva", c(paste0("0", 1:9), 10:12))))
  ) %>% mutate(
    txv01 = rowSums(across(starts_with("txv01")  & !contains("_na"))), 
    txv02 = rowSums(across(starts_with("txv02")  & !contains("_na"))),
    txv03 = rowSums(across(starts_with("txv03")  & !contains("_na"))), 
    txv04 = rowSums(across(starts_with("txv04")  & !contains("_na"))),
    txv05 = rowSums(across(starts_with("txv05")  & !contains("_na"))),
    txv06 = rowSums(across(starts_with("txv06")  & !contains("_na"))),
    txv07 = rowSums(across(starts_with("txv07")  & !contains("_na"))),
    txv08 = rowSums(across(starts_with("txv08")  & !contains("_na"))),
    txv09 = rowSums(across(starts_with("txv09")  & !contains("_na"))),
    txv10 = rowSums(across(starts_with("txv10")  & !contains("_na"))),
    txv11 = rowSums(across(starts_with("txv11")  & !contains("_na"))),
    txv12 = rowSums(across(starts_with("txv12")  & !contains("_na"))),
    txv_tot = rowSums(across(paste0("txv", c(paste0("0", 1:9), 10:12))))
  ) %>% mutate(
    txa01 = rowSums(across(starts_with("txa01")  & !contains("_na"))), 
    txa02 = rowSums(across(starts_with("txa02")  & !contains("_na"))),
    txa03 = rowSums(across(starts_with("txa03")  & !contains("_na"))), 
    txa04 = rowSums(across(starts_with("txa04")  & !contains("_na"))),
    txa05 = rowSums(across(starts_with("txa05")  & !contains("_na"))),
    txa06 = rowSums(across(starts_with("txa06")  & !contains("_na"))),
    txa07 = rowSums(across(starts_with("txa07")  & !contains("_na"))),
    txa08 = rowSums(across(starts_with("txa08")  & !contains("_na"))),
    txa09 = rowSums(across(starts_with("txa09")  & !contains("_na"))),
    txa10 = rowSums(across(starts_with("txa10")  & !contains("_na"))),
    txa11 = rowSums(across(starts_with("txa11")  & !contains("_na"))),
    txa12 = rowSums(across(starts_with("txa12")  & !contains("_na"))),
    txa_tot = rowSums(across(paste0("txa", c(paste0("0", 1:9), 10:12))))
  )
  em_data <- em_data %>% group_by(idhh) %>% mutate(
    across(c(paste0("dx", c(paste0("0", 1:9), 10:12, "_tot")),
             paste0("dxx", c(paste0("0", 1:9), 10:12, "_tot")),
             paste0("tva", c(paste0("0", 1:9), 10:12, "_tot")),
             paste0("txv", c(paste0("0", 1:9), 10:12, "_tot")),
             paste0("txa", c(paste0("0", 1:9), 10:12, "_tot")),
             ils_origy, ils_tax, ils_sicdy, ils_ben, ils_pen, ils_dispy, il_taxabley_bf_mq, tin_s, tinna_s),
           sum,
           .names = "HH{.col}")) %>% ungroup()
  return(em_data)
}


## ----f_sumtabLS-----------------------------------------------------------------------------------------------------
f_sumtabLS <- function(df_tab, groupingvars, reform, folder, wri){
  if (reform == 1){
    df_tmp <- df_tab %>% rename_at(vars(contains("_r1")), ~ (str_replace(., "_r1", "_r")))
  }
  if (reform == 2){
    df_tmp <- df_tab %>% rename_at(vars(contains("_r2")), ~ (str_replace(., "_r2", "_r")))
  }
  if (is_empty(groupingvars)){
    sumtabLS <- df_tmp %>% summarise(
      freq = sum(dwt.obs), 
      participatie_b = sum(ifelse(working.obs > 0, dwt.obs, 0)),
      participatie_r = sum(ifelse(working.exp_r > 0, dwt.obs*working.exp_r, 0)),
      rel_participatie = participatie_r/participatie_b - 1, 
      uren_b_FTE = sum(hours.obs * dwt.obs)/38, 
      uren_r_FTE = sum(hours.exp_r * dwt.obs)/38,
      rel_uren = uren_r_FTE/uren_b_FTE - 1, 
      
      "delta uren (FTE)"= sum(difh_r*dwt.obs)/38, 
      "uren intensieve marge (FTE)" = sum(difh_im_r * dwt.obs)/38,
      "uren intensieve marge pos (FTE)"= sum(ifelse(difh_im_r > 0, difh_im_r, 0)*dwt.obs)/38,
      "uren intensieve marge neg (FTE)"= sum(ifelse(difh_im_r < 0, difh_im_r, 0)*dwt.obs)/38,
      "uren extensieve marge (FTE)"= sum(difh_em_r*dwt.obs)/38,
      "uren extensieve marge in (FTE)"= sum(ifelse(difh_em_r > 0, difh_em_r, 0)*dwt.obs)/38, 
      "uren extensieve marge out (FTE)"= sum(ifelse(difh_em_r < 0, difh_em_r, 0)*dwt.obs)/38, 
      
      "reacties" = sum(ifelse(difh_im_r != 0| difh_em_r > 0, dwt.obs*working.exp_r, 0) + ifelse(difh_em_r < 0, dwt.obs*(1-working.exp_r), 0)),
      "reacties intensieve marge" = sum(ifelse(difh_im_r != 0, dwt.obs * working.exp_r, 0)), 
      "reacties intensieve marge pos" = sum(ifelse(difh_im_r > 0, dwt.obs * working.exp_r, 0)),
      "reacties intensieve marge neg" = sum(ifelse(difh_im_r < 0, dwt.obs * working.exp_r, 0)),
      "reacties extensieve marge" = sum(ifelse(difh_em_r > 0, dwt.obs*working.exp_r, 0) + ifelse(difh_em_r < 0, dwt.obs*(1-working.exp_r), 0)), 
      "reacties extensieve marge in" = sum(ifelse(difh_em_r > 0, dwt.obs * working.exp_r, 0)), 
      "reacties extensieve marge out" = sum(ifelse(difh_em_r < 0, dwt.obs * (1-working.exp_r), 0)),
      
      "budget eerste ronde" = sum((-tin_s.for_r + tin_s.obs) * 12 * dwt.obs), 
      "budget tweede ronde" = sum((-tin_s.exp_r + tin_s.for_r) * 12 *dwt.obs),
      "kostprijs per FTE" = sum((-tin_s.exp_r + tin_s.obs) * 12* dwt.obs)/(sum(difh_r * dwt.obs)/38),
      .group = "drop")
  } else {
    sumtabLS <- df_tmp %>% group_by_at(vars(groupingvars)) %>% summarise(
      freq = sum(dwt.obs), 
      participatie_b = sum(ifelse(working.obs > 0, dwt.obs, 0)),
      participatie_r = sum(ifelse(working.exp_r > 0, dwt.obs*working.exp_r, 0)),
      rel_participatie = participatie_r/participatie_b - 1, 
      uren_b_FTE = sum(hours.obs * dwt.obs)/38, 
      uren_r_FTE = sum(hours.exp_r * dwt.obs)/38,
      rel_uren = uren_r_FTE/uren_b_FTE - 1, 
      
      "delta uren (FTE)"= sum(difh_r*dwt.obs)/38, 
      "uren intensieve marge (FTE)" = sum(difh_im_r * dwt.obs)/38,
      "uren intensieve marge pos (FTE)"= sum(ifelse(difh_im_r > 0, difh_im_r, 0)*dwt.obs)/38,
      "uren intensieve marge neg (FTE)"= sum(ifelse(difh_im_r < 0, difh_im_r, 0)*dwt.obs)/38,
      "uren extensieve marge (FTE)"= sum(difh_em_r*dwt.obs)/38,
      "uren extensieve marge in (FTE)"= sum(ifelse(difh_em_r > 0, difh_em_r, 0)*dwt.obs)/38, 
      "uren extensieve marge out (FTE)"= sum(ifelse(difh_em_r < 0, difh_em_r, 0)*dwt.obs)/38, 
      
      "reacties" = sum(ifelse(difh_im_r != 0| difh_em_r > 0, dwt.obs*working.exp_r, 0) + ifelse(difh_em_r < 0, dwt.obs*(1-working.exp_r), 0)),
      "reacties intensieve marge" = sum(ifelse(difh_im_r != 0, dwt.obs * working.exp_r, 0)), 
      "reacties intensieve marge pos" = sum(ifelse(difh_im_r > 0, dwt.obs * working.exp_r, 0)),
      "reacties intensieve marge neg" = sum(ifelse(difh_im_r < 0, dwt.obs * working.exp_r, 0)),
      "reacties extensieve marge" = sum(ifelse(difh_em_r > 0, dwt.obs*working.exp_r, 0) + ifelse(difh_em_r < 0, dwt.obs*(1-working.exp_r), 0)), 
      "reacties extensieve marge in" = sum(ifelse(difh_em_r > 0, dwt.obs * working.exp_r, 0)), 
      "reacties extensieve marge out" = sum(ifelse(difh_em_r < 0, dwt.obs * (1-working.exp_r), 0)),
      
      "budget eerste ronde" = sum((-tin_s.for_r + tin_s.obs) * 12 * dwt.obs), 
      "budget tweede ronde" = sum((-tin_s.exp_r + tin_s.for_r) * 12 * dwt.obs),
      "kostprijs per FTE" = sum((-tin_s.exp_r + tin_s.obs) * 12 * dwt.obs)/(sum(difh_r * dwt.obs)/38),
      .groups = "drop")
  }
  write.csv2(sumtabLS, paste0(folder, "/sumtabLS/sumtabLS_", ifelse(wri, "wri_", "wai_"), paste(groupingvars, collapse = "_"), "_r", reform,".csv"))
}
ff_sumtabLS <- function(df_tab, groupingvars, wri){
  f_sumtabLS(df_tab, groupingvars = groupingvars, reform = 1, outputfolder, wri)
  f_sumtabLS(df_tab, groupingvars = groupingvars, reform = 2, outputfolder, wri)
}

