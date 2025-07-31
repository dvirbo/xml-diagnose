BEGIN TRANSACTION;


CREATE TABLE [actone].[dbo].IMP_REPORT_STATUS_TRACKING (
    report_id INT NOT NULL,
    alert_id VARCHAR(50) NOT NULL,
    update_date DATETIME,
    [status] VARCHAR(50),
    comments VARCHAR(500),
    tech_comment VARCHAR(50),
    business_comment VARCHAR(50)
);

CREATE TABLE [actone].[dbo].IMP_REPORT_PROCESSES_LOG (
    start_time DATETIME,
    end_time DATETIME,
    report_id INT NOT NULL,
    alert_id VARCHAR(50) NOT NULL,
    sar_folder_name VARCHAR(255)
)

COMMIT TRANSACTION;


