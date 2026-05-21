import useAxios from '@base-lib/hooks/core/useAxios'
import type { AlarmAuditModel, AlarmFormModel, AlarmListItemModel, AlarmQueryModel } from '../model'

const request = useAxios()

export const loadPage = (params: AlarmQueryModel) => {
  return request.get<ResPage<AlarmListItemModel>>({
    url: `/zl-business/alarm/record/page`,
    params: {
      ...params,
      pageOrder: 'create_time desc'
    }
  })
}

export const add = (data: AlarmFormModel) => {
  return request.post({
    url: `/zl-business/alarm/record`,
    data
  })
}

export const update = (data: AlarmFormModel) => {
  return request.put({
    url: `/zl-business/alarm/record`,
    data
  })
}

export const audit = (data: AlarmAuditModel) => {
  return request.put({
    url: `/zl-business/alarm/record/audit`,
    data
  })
}
