import useAxios from '@base-lib/hooks/core/useAxios'
import type { AlarmVO, AlarmQueryModel, AlarmFormModel } from '../model'

const request = useAxios()

/** 分页查询 */
export const loadPage = (params: AlarmQueryModel) => {
  return request.get<ResPage<AlarmVO>>({
    url: `/zl-business/alarm/record/page`,
    params: {
      ...params,
      pageOrder: 'create_time desc'
    }
  })
}

/** 新增 */
export const add = (data: AlarmFormModel) => {
  return request.post({
    url: `/zl-business/alarm/record`,
    data
  })
}

/** 更新 */
export const update = (data: AlarmFormModel) => {
  return request.put({
    url: `/zl-business/alarm/record`,
    data
  })
}

/** 删除 */
export const removeById = (id: string) => {
  return request.delete({
    url: `/zl-business/alarm/record/${id}`
  })
}
