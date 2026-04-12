-- 1. Create the Raw Sensor Data table
-- This stores the incoming JSON telemetry from the Aggregator node.
CREATE TABLE raw_sensor_data (
    id INT PRIMARY KEY IDENTITY(1,1),
    sensor_id VARCHAR(50) NOT NULL,
    json_payload NVARCHAR(MAX) NOT NULL, -- Stores the "neatly packaged" JSON
    timestamp DATETIME2 DEFAULT SYSUTCDATETIME()
);

-- 2. Create the Predictions table
-- Stores ML results with a foreign key back to the specific raw data used.
CREATE TABLE predictions (
    prediction_id INT PRIMARY KEY IDENTITY(1,1),
    raw_data_id INT NOT NULL,
    prediction_value FLOAT NOT NULL,
    model_version VARCHAR(20),
    created_at DATETIME2 DEFAULT SYSUTCDATETIME(),
    
    -- Define Relationships
    CONSTRAINT FK_RawData FOREIGN KEY (raw_data_id) 
    REFERENCES raw_sensor_data(id) ON DELETE CASCADE
);

-- 3. Define Indexes
-- Essential for fast historical queries and ML inference speed
CREATE INDEX IX_SensorData_Timestamp ON raw_sensor_data(timestamp);
CREATE INDEX IX_Predictions_RawDataID ON predictions(raw_data_id);

GO
-- data retention: cleanup of data older than 30 days
CREATE PROCEDURE sp_CleanupOldData
AS
BEGIN
    DELETE FROM raw_sensor_data 
    WHERE timestamp < DATEADD(day, -30, GETDATE());
    -- Cascading delete will automatically remove associated predictions.
END;
GO