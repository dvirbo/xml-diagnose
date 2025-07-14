-- Create table IMP_REPORT_LOG
CREATE TABLE dbo.IMP_REPORT_LOG (
    Report_id  NUMBER NOT NULL,
    Alert_id  VARCHAR(50) NOT NULL,
    Report_date DATETIME,
    [Status] VARCHAR(50),
    Comments VARCHAR(500),
    Received_date DATETIME,
    Mispar_tkina VARCHAR(50),
    Status_divuah VARCHAR(50),
    PRIMARY KEY (Report_id, Alert_id, Report_date,[Status])
);

-- Create table IMP_REPORT_STATUS_TRACKING
CREATE TABLE IMP_REPORT_STATUS_TRACKING (
    Report_id NUMBER NOT NULL,
    Alert_id VARCHAR(50) NOT NULL,
    Update_date DATETIME,
    [Status] VARCHAR(50),
    Comments VARCHAR(500),
    FOREIGN KEY (Report_id, Alert_id) REFERENCES IMP_REPORT_LOG(Report_id, Alert_id)
);


 