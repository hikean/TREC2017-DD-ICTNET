# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/8 下午3:46
# @version: 1.0


from xml.dom.minidom import Document


# 将self.orderDict中的信息写入本地xml文件，参数filename是xml文件名
def writeInfoToXml(self, filename):
    # 创建dom文档
    doc = Document()

    # 创建根节点
    orderlist = doc.createElement('orderlist')
    # 根节点插入dom树
    doc.appendChild(orderlist)

    # 依次将orderDict中的每一组元素提取出来，创建对应节点并插入dom树
    for (k, v) in self.orderDict.iteritems():
        # 分离出姓名，电话，地址，点餐次数
        (name, tel, addr, cnt) = (v[0], k, v[1], v[2])

        # 每一组信息先创建节点<order>，然后插入到父节点<orderlist>下
        order = doc.createElement('order')
        orderlist.appendChild(order)

        # 将姓名插入<order>中
        # 创建节点<customer>
        customer = doc.createElement('customer')
        # 创建<customer>下的文本节点
        customer_text = doc.createTextNode(name)
        # 将文本节点插入到<customer>下
        customer.appendChild(customer_text)
        # 将<customer>插入到父节点<order>下
        order.appendChild(customer)

        # 将电话插入<order>中，处理同上
        phone = doc.createElement('phone')
        phone_text = doc.createTextNode(tel)
        phone.appendChild(phone_text)
        order.appendChild(phone)

        # 将地址插入<order>中，处理同上
        address = doc.createElement('address')
        address_text = doc.createTextNode(addr)
        address.appendChild(address_text)
        order.appendChild(address)

        # 将点餐次数插入<order>中，处理同上
        count = doc.createElement('count')
        count_text = doc.createTextNode(str(cnt))
        count.appendChild(count_text)
        order.appendChild(count)

    # 将dom对象写入本地xml文件
    with open(filename, 'w') as f:
        f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))

    return


if __name__ == '__main__':
    pass

__END__ = True
