function add_binds(tagName) {
    x = document.getElementsByTagName(tagName);
    for (i = 0, l = x.length; i < l; i++) {
        // x[i].addEventListener('click', click_bind);
        x[i].addEventListener('mousedown', click_bind)

    }
}

function remove_binds(tagName) {
    x = document.getElementsByTagName(tagName);
    for (i = 0, l = x.length; i < l; i++) {
        // x[i].removeEventListener('click', click_bind);
        x[i].removeEventListener('mousedown', click_bind);
    }
}


function click_bind() {
    console.log(this);
    // console.log(this.id);

    console.log(readXPath(this));
    var Dict = { 'data': this, 'seleniumXpath': readXPath(this) };

    for (var item in this) {
        if (this[item]) {
            Dict[item] = this[item];
        }
    }
    var data = JSON.stringify(Dict);

    Ajax.post('https://127.0.0.1:5000/', data, call_back)
}

//获取xpath
function readXPath(element) {
    if (element.id !== "") { //判断id属性，如果这个元素有id，则显 示//*[@id="xPath"]  形式内容
        return '//*[@id=\"' + element.id + '\"]';
    }
    //这里需要需要主要字符串转译问题，可参考js 动态生成html时字符串和变量转译（注意引号的作用）
    if (element == document.body) { //递归到body处，结束递归
        return '/html/' + element.tagName.toLowerCase();
    }
    var ix = 1, //在nodelist中的位置，且每次点击初始化
        siblings = element.parentNode.childNodes; //同级的子元素

    for (var i = 0, l = siblings.length; i < l; i++) {
        var sibling = siblings[i];
        //如果这个元素是siblings数组中的元素，则执行递归操作
        if (sibling == element) {
            return arguments.callee(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix) + ']';
            //如果不符合，判断是否是element元素，并且是否是相同元素，如果是相同的就开始累加
        } else if (sibling.nodeType == 1 && sibling.tagName == element.tagName) {
            ix++;
        }
    }
};

function call_back(text) {
    console.log(text);
}


var Ajax = {
    get: function(url, callback) {
        // XMLHttpRequest对象用于在后台与服务器交换数据
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, false);
        xhr.onreadystatechange = function() {
            // readyState == 4说明请求已完成
            if (xhr.readyState == 4) {
                if (xhr.status == 200 || xhr.status == 304) {
                    console.log(xhr.responseText);
                    callback(xhr.responseText);
                }
            }
        }
        xhr.send();
    },

    // data应为'a=a1&b=b1'这种字符串格式，在jq里如果data为对象会自动将对象转成这种字符串格式
    post: function(url, data, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', url, false);
        // 添加http头，发送信息至服务器时内容编码类型
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200 || xhr.status == 304) {
                    // console.log(xhr.responseText);
                    callback(xhr.responseText);
                }
            }
        }
        xhr.send(data);
    }
}


// click_binds('select');
// click_binds('button');
// click_binds('input');
// click_binds('textarea')