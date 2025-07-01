create table crm_ScheduleHistory(
	Id int primary key identity,
	JobId int,
	JobType nvarchar(20),
	ScheduleTime datetime,
	JobStatus nvarchar(1) default 'S' -- 'S' is stoped, 'W' is waiting, 'R' is running and 'D' is done
)
go

create or alter proc sp_crm_InsertOrUpdateScheduleHistory
@JobId int,
@JobType nvarchar(20),
@ScheduleTime datetime,
@JobStatus nvarchar(1)
as
begin
	if exists (select * from crm_ScheduleHistory where JobId = @JobId)
	begin
		insert into crm_ScheduleHistory (JobId, JobType, ScheduleTime, JobStatus)
		values (@JobId, @JobType, @ScheduleTime, @JobStatus)
	end
	else
	begin
		update crm_ScheduleHistory
		set JobType = @JobType,
			ScheduleTime = @ScheduleTime,
			JobStatus = @JobStatus
		where JobId = @JobId
	end
end
go

-- exec sp_crm_GetCampaignSettingById 29
create or alter proc sp_crm_GetCampaignSettingById
	@SettingId int
as
begin
	select
		RECORD_NUMBER as SettingID,
		text_1_copy_3 as CampaignName,
		drop_down_1 as ReceiverListID,
		drop_down_1_copy_5 as EmailTemplateID,
		text_1 as SMTPServer,
		text_1_copy_4 as SMTPPort,
		text_1_copy_1 as SMTPEmail,
		text_1_copy_2 as SMTPPass
	from AppCreator_be2bea7b
	where RECORD_NUMBER = @SettingId
end
go

-- exec sp_crm_GetTimeScheduleById 36
create or alter proc sp_crm_GetTimeScheduleById
	@SettingId int
as
begin
	select 
        datepart(hour, time_1) as [Hour],
        datepart(minute, time_1) as [Minute],
        radio_button_1 as [ScheduleType]
	from AppCreator_be2bea7b where RECORD_NUMBER = @SettingId
end
go

-- exec sp_crm_GetListReceiverNeedSend 36
create or alter proc sp_crm_GetListReceiverNeedSend
	@SettingId int
as
begin
	select 
		t0.Campaign_ID as [CampaignId],
		t0.RECORD_NUMBER as [DashboardId],
		t1.text_3 as Email,
		t1.text_2 as FullName,
		t1.text_4 as Company,
		t1.text_5 as Phone
	from (
		select t3.Campaign_ID, t2.* from AppCreator_9e421964_table_1 t2
		left join AppCreator_9e421964 t3 on t2.RECORD_NUMBER = t3.RECORD_NUMBER
	) t0
	right join AppCreator_4a9f8a7c_table_1 t1 on t0.text_3 = t1.text_3 and t0.text_2 = t1.text_2
	where t0.Campaign_ID = @SettingId --and t0.text_4 = 'FALSE'
end
go

-- exec sp_crm_GetImportReceiverFile 2
create or alter proc sp_crm_GetImportReceiverFile
	@ListId int
as
begin
	select t0.*, t1.text_6 as [LIST_NAME] from AppCreator_4a9f8a7c_CsvContent t0
	left join AppCreator_4a9f8a7c t1 on t0.RECORD_NUMBER = t1.RECORD_NUMBER
	where t0.RECORD_NUMBER = @ListId
end
go

--select * from AppCreator_4a9f8a7c_table_1 where RECORD_NUMBER = 2
drop proc if exists sp_crm_ImportReceiverAction
go
drop type if exists type_crm_ImportReceiverAction
go
create type type_crm_ImportReceiverAction as table (
	Fullname nvarchar(200),
	Email nvarchar(200),
	Company nvarchar(200),
	Phone nvarchar(200)
)
go
create proc sp_crm_ImportReceiverAction
	@ListId int,
	@Data type_crm_ImportReceiverAction readonly
as
begin
	delete from AppCreator_4a9f8a7c_table_1 where RECORD_NUMBER = @ListId
	insert into AppCreator_4a9f8a7c_table_1 (RECORD_NUMBER, text_1, text_2, text_3, text_4, text_5)
	select 
		@ListId,
		row_number() over (order by (select null)), 
		Fullname, 
		Email, 
		Company, 
		Phone 
	from @Data
end
go

create or alter proc sp_crm_CampaignSettingStatusAction
	@SettingId int,
	@Status int
as
begin
	update AppCreator_be2bea7b
		set radio_button_2 = @Status
    where RECORD_NUMBER = @SettingId
end
go

create or alter proc sp_crm_CampaignDashboardStatusAction
	@SettingId int,
	@Email nvarchar(100),
	@UpdateColumn  nvarchar(30),
	@Status nvarchar(30)
as
begin
	declare @action nvarchar(max)
	set @action = '
	update AppCreator_9e421964_table_1
		set ' + quotename(@UpdateColumn) + ' = @Status
	where text_3 = @Email and RECORD_NUMBER = (select top 1 RECORD_NUMBER from AppCreator_9e421964 where Campaign_ID = @SettingId)
	'
	exec sp_executesql 
		@action, 
		N'@SettingId int, @Email nvarchar(100), @Status nvarchar(30)',
		@SettingId = @SettingId,
		@Email = @Email,
		@Status = @Status
end
go