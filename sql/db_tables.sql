-- Create table IMP_REPORT_LOG
CREATE TABLE dbo.IMP_REPORT_LOG (
    Report_id INT NOT NULL,
    Alert_id  VARCHAR(50) NOT NULL,
    Report_date DATETIME,
    Comments VARCHAR(500),
    Received_date DATETIME,
    Mispar_tkina VARCHAR(50),
    Status_divuah VARCHAR(50),
);

-- Create table IMP_REPORT_STATUS_TRACKING
CREATE TABLE IMP_REPORT_STATUS_TRACKING (
    Report_id INT NOT NULL,
    Alert_id VARCHAR(50) NOT NULL,
    Update_date DATETIME,
    [Status] VARCHAR(50),
    Comments VARCHAR(500),
);


   select *  
    FROM [actone].[dbo].[alerts]
    where alert_id = 'SAM1-1781'

select *
from [actone].[dbo].IMP_REPORT_STATUS_TRACKING



--523670
select *
from [actone].[dbo].IMP_REPORT_STATUS_TRACKING

-- add Folder_name column to IMP_REPORT_LOG:
alter table [actone].[dbo].IMP_REPORT_STATUS_TRACKING 
ADD folder_name VARCHAR(255);



-- select Folder_name from [actone].[dbo].IMP_REPORT_LOG  
-- where 