SELECT TOP (1000) [alert_internal_id]
      ,[entity_type_id]
      ,[alert_date]
      ,[alert_type_id]
      ,[status_id]
  FROM [actone].[dbo].[alerts]
  WHERE [alert_id] = 'SAM1-2025'

--   select top (2) *
--   from [dbo].[acm_alert_custom_attributes]
   
-- select top (12) *
-- from alerts

-- select * from
-- [dbo].[acm_md_alert_statuses]

SELECT *
from [actone].[dbo].[IMP_REPORT_STATUS_TRACKING]

insert into [actone].[dbo].[IMP_REPORT_LOG]
    ([Report_id]
    ,[Alert_id])
values
    (0523670, 'SAM1-1782')

        SELECT * 
        FROM [actone].[dbo].[IMP_REPORT_LOG]
        WHERE report_id = 0523670


        SELECT DISTINCT report_id, alert_id  FROM [actone].[dbo].[IMP_REPORT_LOG] 
        WHERE report_id IN (0523670,05236,052367)


select *
from [actone].[dbo].[IMP_REPORT_LOG]
where alert_id = 'SAM1-2194'
