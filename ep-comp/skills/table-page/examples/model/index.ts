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

  @FieldName('入库时间')
  createTime!: string

  id!: string
}
