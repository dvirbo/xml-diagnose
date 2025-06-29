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