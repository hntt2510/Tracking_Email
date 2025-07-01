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
