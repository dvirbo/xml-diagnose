
/*

CREATE TABLE [actone].[dbo].IMP_REPORT_STATUS_TRACKING (
    report_id INT NOT NULL,
    alert_id VARCHAR(50) NOT NULL,
    update_date DATETIME,
    [status] VARCHAR(50),
    comments VARCHAR(500),
    first_response_valid BIT,
    final_response_valid BIT
);

CREATE TABLE [actone].[dbo].IMP_REPORT_PROCESSES_LOG (
    start_time DATETIME,
    end_time DATETIME,
    report_id INT NOT NULL,
    alert_id VARCHAR(50) NOT NULL,
    sar_folder_name VARCHAR(255),
    XML_Generic BIT, 
    count_account INT
)

CREATE TABLE [actone].[dbo].IMP_REPORT_LOG (
    report_id INT NOT NULL,
    alert_id VARCHAR(50) NOT NULL,
    report_date DATETIME, 
    first_response_valid BIT ,
    final_response_valid BIT,
    received_date DATETIME, 
    mispar_tkina INT,
    sar_folder_name VARCHAR(50),
)


CREATE TABLE [actone].[dbo].IMP_REPORT_LOG (
    report_id INT NOT NULL,
    alert_id VARCHAR(50) NOT NULL,
    report_date DATETIME, 
    first_response_valid BIT ,
    final_response_valid BIT,
    received_date DATETIME, 
    mispar_tkina INT,
    sar_folder_name VARCHAR(50),
)

BEGIN TRANSACTION
COMMIT TRANSACTION;
*/


-- need to run this..

drop table [actone].[dbo].IMP_REPORT_STATUS_TRACKING

CREATE TABLE [actone].[dbo].IMP_REPORT_STATUS_TRACKING (
    report_id INT NOT NULL,
    alert_id VARCHAR(50) NOT NULL,
    update_date DATETIME,
    [status] VARCHAR(50),
    comments VARCHAR(500),
    first_response_valid BIT,
    final_response_valid BIT
);
