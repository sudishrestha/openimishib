USE [SSF_IMIS_DEMO]
GO
/****** Object:  StoredProcedure [dbo].[generateClaimCode]    Script Date: 1/24/2022 12:27:19 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		<Author,,Name>
-- Create date: <Create Date,,>
-- Description:	<Description,,>
-- =============================================
Create PROCEDURE [dbo].[generateClaimCode]
	-- Add the parameters for the stored procedure here
	
(
	@year  Varchar(20)
	 
)
AS
BEGIN
	-- select CONCAT(@year,RIGHT('00000000'+CAST((count(*) +1) AS VARCHAR(8)),8)) from tblClaim where ClaimCode like @year+'%';
	select CONCAT(@year,RIGHT('00000000'+CAST((count(*) +1) AS VARCHAR(8)),8)) from tblClaim where ClaimCode like @year+'%';
END
