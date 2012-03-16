alter table survey_basicfoodsurvey add column regret integer;
alter table survey_basicfoodsurvey add column expert integer;
alter table survey_basicfoodsurvey add column yelp integer;
alter table survey_basicfoodsurvey add column yelp_community integer;
alter table survey_basicfoodsurvey add column share integer;
alter table survey_basicfoodsurvey alter different set default null;
alter table survey_basicfoodsurvey alter different type integer using case when false then 0 else 1 end;

alter table survey_eatingcompanysurvey add column together integer;
alter table survey_eatingcompanysurvey alter lunch_alone set default null;
alter table survey_eatingcompanysurvey alter lunch_alone type integer using case when false then 0 else 1 end;
alter table survey_eatingcompanysurvey alter lunch_alone set default 0;

alter table survey_eatingoutsurvey add column cheap integer;

alter table survey_eatingoutsurvey add column health integer;

alter table survey_eatingoutsurvey add column regret integer;
alter table survey_eatingoutsurvey add column popular integer;
alter table survey_eatingoutsurvey add column expensive integer;
alter table survey_eatingoutsurvey add column taste integer;
alter table survey_eatingoutsurvey alter plan set default null;
alter table survey_eatingoutsurvey alter plan type integer using case when false then 0 else 1 end;
alter table survey_eatingoutsurvey alter plan set default 0;

