import { FieldName } from '@gx-web/core'

export class AlarmQueryModel {
  @FieldName('设备SN')
  deviceSn!: string
}

export class AlarmListItemModel {
  @FieldName('告警代码')
  alarmCode!: string

  @FieldName('告警标题')
  alarmTitle!: string

  id!: string
}

export class AlarmFormModel {
  @FieldName('告警代码')
  alarmCode!: string

  @FieldName('告警标题')
  alarmTitle!: string

  @FieldName('告警详情')
  alarmDetail!: string

  id!: string
}

export class AlarmAuditModel {
  @FieldName('审批状态')
  approveStatus!: number

  @FieldName('审批备注')
  approveRemark!: string

  id!: string
}
