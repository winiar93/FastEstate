IF NOT EXISTS(SELECT * FROM sys.databases WHERE name = 'otodom')
  BEGIN
    CREATE DATABASE [otodom]

    END
    GO
       USE [otodom]
    GO
--You need to check if the table exists
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='flat_offers' and xtype='U')
BEGIN
    CREATE TABLE flat_offers (
        offer_id INT PRIMARY KEY,
        offer_title NVARCHAR(500),
        street NVARCHAR(500),
        location NVARCHAR(500),
        total_price VARCHAR(10),
        area_square_meters VARCHAR(10),
        date_created NVARCHAR(100),
        offer_url VARCHAR(500),
        agency_name NVARCHAR(500),
        rooms_number VARCHAR(10),
        investment_estimated_delivery NVARCHAR(100),
        price_per_square_meter VARCHAR(10)
    )
END