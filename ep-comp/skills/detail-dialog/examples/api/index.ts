import useAxios from '@base-lib/hooks/core/useAxios'
import type { AlarmDetailModel, AlarmListItemModel, AlarmQueryModel } from '../model'

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

export const loadDetail = (id: string) => {
  return request.get<Res<AlarmDetailModel>>({
    url: `/zl-business/alarm/record/${id}`
  })
}
