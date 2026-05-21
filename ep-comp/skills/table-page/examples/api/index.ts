import useAxios from '@base-lib/hooks/core/useAxios'
import type { AlarmListItemModel, AlarmQueryModel } from '../model'

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
