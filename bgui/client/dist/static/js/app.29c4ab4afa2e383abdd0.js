webpackJsonp([1],{NHnr:function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var r=a("Xxa5"),s=a.n(r),n=a("exGp"),o=a.n(n),i=a("7+uW"),l=a("Lgyv"),u=a.n(l),c="http://localhost:3000",d="AuTuMN TB-modelling",p=!1,m=a("mvHQ"),v=a.n(m),h=a("M4fF"),f=a.n(h),g=a("0hgu"),w=a.n(g),y=a("//Fk"),b=a.n(y),_=a("BO1k"),j=a.n(_),x=function(e){return v()(e,null,2)},k=function(e,t){for(var a=[],r=0;r<e;r+=1)a.push(t);return a},P=function(e){return new b.a(function(t){setTimeout(function(){t(e)},e)})},S=a("Gu7T"),C=a.n(S),R=a("mtWM"),D=a.n(R),U=a("lDdF"),F=a.n(U);D.a.defaults.withCredentials=!0;var z={rpcRun:function(e){for(var t=this,a=arguments.length,r=Array(a>1?a-1:0),n=1;n<a;n++)r[n-1]=arguments[n];return o()(s.a.mark(function a(){var n,o,i;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return o={method:e,params:r,jsonrpc:"2.0"},(n=console).log.apply(n,["> rpc.rpcRun",e].concat(C()(r))),t.prev=2,t.next=5,D.a.post(c+"/api/rpc-run",o);case 5:return i=t.sent,t.abrupt("return",i.data);case 9:return t.prev=9,t.t0=t.catch(2),t.abrupt("return",{error:{code:-32e3,message:t.t0.toString()}});case 12:case"end":return t.stop()}},a,t,[[2,9]])}))()},rpcUpload:function(e,t){for(var a=arguments.length,r=Array(a>2?a-2:0),n=2;n<a;n++)r[n-2]=arguments[n];var i=this;return o()(s.a.mark(function a(){var n,o,l,u,d,p,m,h,f;return s.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:for((o=new FormData).append("method",e),o.append("params",v()(r)),o.append("jsonrpc","2.0"),l=!0,u=!1,d=void 0,a.prev=7,p=j()(t);!(l=(m=p.next()).done);l=!0)h=m.value,o.append("uploadFiles",h,h.name);a.next=15;break;case 11:a.prev=11,a.t0=a.catch(7),u=!0,d=a.t0;case 15:a.prev=15,a.prev=16,!l&&p.return&&p.return();case 18:if(a.prev=18,!u){a.next=21;break}throw d;case 21:return a.finish(18);case 22:return a.finish(15);case 23:return(n=console).log.apply(n,["> rpc.rpcUpoad",e,t].concat(C()(r))),a.prev=24,a.next=27,D.a.post(c+"/api/rpc-upload",o);case 27:return f=a.sent,a.abrupt("return",f.data);case 31:return a.prev=31,a.t1=a.catch(24),a.abrupt("return",{error:{code:-32e3,message:a.t1.toString()}});case 34:case"end":return a.stop()}},a,i,[[7,11,15,23],[16,,18,22],[24,31]])}))()},rpcDownload:function(e){for(var t=this,a=arguments.length,r=Array(a>1?a-1:0),n=1;n<a;n++)r[n-1]=arguments[n];return o()(s.a.mark(function a(){var n,o,i,l,u,d;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return o={method:e,params:r,jsonrpc:"2.0"},(n=console).log.apply(n,["> rpc.rpcDownload"].concat(C()(r))),t.prev=2,t.next=5,D.a.post(c+"/api/rpc-download",o);case 5:return i=t.sent,l=i.headers.filename,u=JSON.parse(i.headers.data),console.log("> rpc.rpcDownload response",u),u.error||(d=new Blob([i.data]),F.a.saveAs(d,l)),t.abrupt("return",u);case 13:return t.prev=13,t.t0=t.catch(2),t.abrupt("return",{error:{code:-32e3,message:t.t0.toString()}});case 16:case"end":return t.stop()}},a,t,[[2,13]])}))()}},E=a("NYxO");i.default.use(E.a);var L=new E.a.Store({state:{user:{authenticated:!1}},mutations:{setUser:function(e,t){e.user=t}}});function G(e){var t=f.a.cloneDeep(e);return!t.password&&t.rawPassword&&(t.password=w()(t.rawPassword).toString(),delete t.rawPassword),t.rawPasswordConfirm&&delete t.rawPasswordConfirm,t}var N={login:function(e){var t=this;return o()(s.a.mark(function a(){var r,n,o;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return r=G(e),console.log("> auth.login",r),t.next=4,z.rpcRun("publicLoginUser",r);case 4:return n=t.sent,console.log("> auth.login response",n),n.result&&(o=f.a.cloneDeep(L.state.user),f.a.assign(o,n.result.user),o.authenticated=!0,o.password=r.password,localStorage.setItem("user",x(o)),L.commit("setUser",o)),t.abrupt("return",n);case 8:case"end":return t.stop()}},a,t)}))()},register:function(e){var t=G(e);return console.log("> auth.register",t),z.rpcRun("publicRegisterUser",t)},update:function(e){var t=this;return o()(s.a.mark(function a(){var r,n,o;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return r=G(e),console.log("> auth.update",x(r)),t.next=4,z.rpcRun("loginUpdateUser",r);case 4:return(n=t.sent).result&&(o=f.a.cloneDeep(L.state.user),f.a.assign(o,r),localStorage.setItem("user",v()(o)),L.commit("setUser",o)),t.abrupt("return",n);case 7:case"end":return t.stop()}},a,t)}))()},resetPassword:function(e,t){var a=this;return o()(s.a.mark(function r(){var n;return s.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return n=w()(t).toString(),console.log("> auth.resetPassword",e,n),a.abrupt("return",z.rpcRun("publicForceUpdatePassword",e,n));case 3:case"end":return a.stop()}},r,a)}))()},restoreLastUser:function(){var e=this;return o()(s.a.mark(function t(){var a;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:if(a=JSON.parse(localStorage.getItem("user")),console.log("> auth.restoreLastUser from localStorage",a),!a){t.next=4;break}return t.abrupt("return",e.login(a));case 4:case"end":return t.stop()}},t,e)}))()},logout:function(){return localStorage.removeItem("user"),L.commit("setUser",{authenticated:!1}),z.rpcRun("publicLogoutUser")}},O={name:"navbar",data:function(){return{title:d,isUser:p}},computed:{user:function(){return this.$store.state.user}},methods:{editUser:function(){this.$router.push("/edit-user")},home:function(){this.$router.push("/")},logout:function(){var e=this;return o()(s.a.mark(function t(){return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,N.logout();case 2:e.$router.push("/login");case 3:case"end":return t.stop()}},t,e)}))()}}},A={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("md-toolbar",{staticClass:"md-dense"},[a("md-icon",{attrs:{"md-src":"./static/logo.png"}}),e._v(" "),a("h2",{staticClass:"md-title",staticStyle:{"padding-left":"1em",cursor:"pointer",flex:"1"},on:{click:function(t){e.home()}}},[e._v("\n    "+e._s(e.title)+"\n  ")]),e._v(" "),e.isUser?a("div",[e.user.authenticated?a("md-menu",[a("md-button",{attrs:{"md-menu-trigger":""}},[e._v("\n        "+e._s(e.user.name)+"\n      ")]),e._v(" "),a("md-menu-content",[a("md-menu-item",{on:{click:e.editUser}},[e._v("\n          Edit User\n        ")]),e._v(" "),a("md-menu-item",{on:{click:e.logout}},[e._v("\n          Logout\n        ")])],1)],1):a("router-link",{attrs:{to:"/login",tag:"md-button"}},[e._v("\n      Login\n    ")])],1):e._e()],1)},staticRenderFns:[]},B={name:"app",components:{Navbar:a("VU/8")(O,A,!1,null,null,null).exports}},$={render:function(){var e=this.$createElement,t=this._self._c||e;return t("div",{attrs:{id:"app"}},[t("navbar"),this._v(" "),t("router-view")],1)},staticRenderFns:[]};var q=a("VU/8")(B,$,!1,function(e){a("rpYJ")},null,null).exports,T=a("/ocq"),W=a("GDE4"),M=a.n(W),V=a("bm7V"),H=a.n(V),X=a("Zrlr"),I=a.n(X),J=a("wxAW"),Y=a.n(J),K=a("7t+N"),Q=a.n(K),Z=a("WaEV"),ee=a.n(Z);var te=["#4ABDAC","#FC4A1A","#F78733","#037584","#007849","#FAA43A","#60BD68","#F17CB0","#B2912F","#B276B2","#DECF3F","#F15854","#C08283","#dcd0c0","#E37222"],ae=[];var re=function(){function e(t,a){I()(this,e),this.divTag=t,this.div=Q()(this.divTag);var r,s,n,o=Q()("<canvas>");this.div.append(o),this.chartData=a||{type:"scatter",data:{datasets:[]},options:{title:{display:!0,text:r},legend:{display:!1},maintainAspectRatio:!1,responsive:!0,scales:{xAxes:[{type:"linear",position:"bottom",scaleLabel:{display:!0,labelString:s},ticks:{}}],yAxes:[{type:"linear",scaleLabel:{display:!0,labelString:n}}]}}},this.chart=new ee.a(o,this.chartData)}return Y()(e,[{key:"getDatasets",value:function(){return this.chartData.data.datasets}},{key:"getChartOptions",value:function(){return this.chartData.options}},{key:"addDataset",value:function(e,t,a){var r=arguments.length>3&&void 0!==arguments[3]?arguments[3]:null,s=this.getDatasets(),n=[];if(t&&a)for(var o=0;o<t.length;o+=1)n.push({x:t[o],y:a[o]});var i=s.length;null===r&&(r=function(e){var t=ae.indexOf(e);return t<0&&(ae.push(e),t=ae.length-1),te[t%te.length]}(i));var l={label:e,data:n,fill:!1,backgroundColor:r,borderColor:r,showLine:!1};return s.push(l),this.chart.update(),i}},{key:"updateDataset",value:function(e,t,a){var r=this.getDatasets()[e];r.data.length=0;for(var s=0;s<t.length;s+=1)r.data.push({x:t[s],y:a[s]});this.chart.update()}},{key:"setTitle",value:function(e){this.getChartOptions().title.text=e}},{key:"setXLabel",value:function(e){this.getChartOptions().scales.xAxes[0].scaleLabel.labelString=e}},{key:"setYLabel",value:function(e){this.getChartOptions().scales.yAxes[0].scaleLabel.labelString=e}},{key:"destroy",value:function(){this.chart.destroy(),this.div.empty()}}]),e}();i.default.use(H.a);var se={name:"experiments",components:{vueSlider:M.a},data:function(){return{params:{},paramGroups:[],paramGroup:null,iParamGroup:-1,isRunning:!1,consoleLines:[],filenames:[],project:null,projects:[],imageWidth:50,imageStyle:"width: 50%",isGraph:!1}},created:function(){var e=this;return o()(s.a.mark(function t(){var a;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,z.rpcRun("public_get_autumn_params");case 2:(a=t.sent).result&&(console.log("> Model.created",a.result),e.paramGroups=a.result.paramGroups,e.params=a.result.params,e.defaultParams=f.a.cloneDeep(a.result.params),e.paramGroup=e.paramGroups[0],e.projects=a.result.projects,e.countryDefaults=a.result.countryDefaults),e.charts={},e.isGraph=!1,e.checkRun();case 7:case"end":return t.stop()}},t,e)}))()},methods:{checkRun:function(){var e=this;return o()(s.a.mark(function t(){var a,r;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,z.rpcRun("public_check_autumn_run");case 2:(a=t.sent).result&&(e.consoleLines=a.result.console,e.$el.querySelector&&((r=e.$el.querySelector("#console-output")).scrollTop=r.scrollHeight),f.a.keys(a.result.graph_data).length>0&&(e.isGraph=!0,e.updateGraph(a.result.graph_data))),a.result.is_running?(e.isRunning=!0,setTimeout(e.checkRun,2e3)):e.isRunning=!1;case 5:case"end":return t.stop()}},t,e)}))()},updateGraph:function(e){console.log("> Model.updateGraph");var t=f.a.keys(e.all_parameters_tried),a=!0,r=!1,s=void 0;try{for(var n,o=j()(f.a.range(t.length));!(a=(n=o.next()).done);a=!0){var i=n.value,l=t[i];if(!(l in this.charts)){var u=new re("#temp-chart-"+i);u.setTitle(l),u.setYLabel(""),u.setXLabel("accepted runs"),this.charts[l]=u}var c=this.charts[l],d=e.rejection_dict[l],p=f.a.keys(d),m=0,v=e.all_parameters_tried[l],h=f.a.filter(v,function(t,a){return e.whether_accepted_list[a]}),g=f.a.range(1,h.length+1);m>=c.getDatasets().length?c.addDataset(l,g,h,"#037584"):c.updateDataset(m,g,h);var w=!0,y=!1,b=void 0;try{for(var _,x=j()(p);!(w=(_=x.next()).done);w=!0){var P=_.value;m+=1;var S=d[P],C=k(S.length,parseFloat(P)+1),R=l+P;m>=c.getDatasets().length?c.addDataset(R,C,S,"#FC4A1A"):c.updateDataset(m,C,S)}}catch(e){y=!0,b=e}finally{try{!w&&x.return&&x.return()}finally{if(y)throw b}}}}catch(e){r=!0,s=e}finally{try{!a&&o.return&&o.return()}finally{if(r)throw s}}},deleteBreakpoint:function(e,t,a){this.params[t].value.splice(a,1)},addBreakpoint:function(e,t){this.params[t].value.push(f.a.max(this.params[t].value))},breakpointCallback:function(e,t){var a=this;return o()(s.a.mark(function e(){return s.a.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,P(100);case 2:a.params[t].value=f.a.sortBy(a.params[t].value,function(e){return f.a.parseInt(e)});case 3:case"end":return e.stop()}},e,a)}))()},selectParamGroup:function(e){this.paramGroup=this.paramGroups[e]},run:function(){var e=this;return o()(s.a.mark(function t(){var a,r,n,o,i,l,u,d,p,m,v,h,g,w;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:for(a=f.a.cloneDeep(e.params),r=!0,n=!1,o=void 0,t.prev=4,i=j()(f.a.values(a));!(r=(l=i.next()).done);r=!0)"breakpoints"===(u=l.value).type?u.value=f.a.sortedUniq(u.value):"number"===u.type||"double"===u.type?u.value=parseFloat(u.value):"integer"===u.type&&(u.value=f.a.parseInt(u.value));t.next=12;break;case 8:t.prev=8,t.t0=t.catch(4),n=!0,o=t.t0;case 12:t.prev=12,t.prev=13,!r&&i.return&&i.return();case 15:if(t.prev=15,!n){t.next=18;break}throw o;case 18:return t.finish(15);case 19:return t.finish(12);case 20:for(e.filenames=[],e.isRunning=!0,e.isGraph=!1,e.project="",e.consoleLines=[],d=!0,p=!1,m=void 0,t.prev=28,v=j()(f.a.keys(e.charts));!(d=(h=v.next()).done);d=!0)g=h.value,e.charts[g].destroy(),delete e.charts[g];t.next=36;break;case 32:t.prev=32,t.t1=t.catch(28),p=!0,m=t.t1;case 36:t.prev=36,t.prev=37,!d&&v.return&&v.return();case 39:if(t.prev=39,!p){t.next=42;break}throw m;case 42:return t.finish(39);case 43:return t.finish(36);case 44:return setTimeout(e.checkRun,2e3),t.next=47,z.rpcRun("public_run_autumn",a);case 47:(w=t.sent).result&&w.result.success?(e.project=w.result.project,e.projects.push(e.project),e.filenames=f.a.map(w.result.filenames,function(e){return c+"/file/"+e}),console.log(">> Model.run filenames",e.filenames)):(e.consoleLines.push("Error: model crashed"),e.isRunning=!1);case 49:case"end":return t.stop()}},t,e,[[4,8,12,20],[13,,15,19],[28,32,36,44],[37,,39,43]])}))()},changeProject:function(e){var t=this;return o()(s.a.mark(function a(){var r,n;return s.a.wrap(function(a){for(;;)switch(a.prev=a.next){case 0:return a.next=2,z.rpcRun("public_get_project_images",e);case 2:(r=a.sent).result&&(console.log("> Model.changeProject",e,r.result),t.filenames=f.a.map(r.result.filenames,function(e){return c+"/file/"+e}),t.consoleLines=r.result.consoleLines,t.$el.querySelector&&((n=t.$el.querySelector("#console-output")).scrollTop=n.scrollHeight),r.result.params&&(t.params=r.result.params),console.log("> Model.changeProject",t.filenames));case 4:case"end":return a.stop()}},a,t)}))()},changeWidth:function(){this.imageStyle="width: "+this.imageWidth+"%",console.log("> Model.changeWidth",this.imageStyle)},selectDropDown:function(e){if("country"===e){var t=this.params[e].value.toLowerCase();if(t in this.countryDefaults){var a=this.countryDefaults[t];this.params=f.a.cloneDeep(this.defaultParams);var r=!0,s=!1,n=void 0;try{for(var o,i=j()(f.a.keys(a));!(r=(o=i.next()).done);r=!0){var l=o.value;console.log("> Model.select",t,l,v()(this.params[l].value),"->",v()(a[l].value)),this.params[l].value=a[l].value}}catch(e){s=!0,n=e}finally{try{!r&&i.return&&i.return()}finally{if(s)throw n}}}}}}},ne={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{},[a("md-layout",{attrs:{"md-column":""}},[a("md-layout",{attrs:{"md-row":""}},[a("md-layout",{staticStyle:{width:"50%",height:"calc(100vh - 48px)",overflow:"auto"},attrs:{"md-row":""}},[a("md-whiteframe",{staticStyle:{width:"230px","padding-top":"30px"}},[a("h2",{staticClass:"md-heading",staticStyle:{"padding-left":"15px"}},[e._v("\n            Parameter sets\n          ")]),e._v(" "),a("md-list",e._l(e.paramGroups,function(t,r){return a("md-list-item",{key:r,attrs:{id:t.name},on:{click:function(t){e.selectParamGroup(r)}}},[e._v("\n              "+e._s(t.name)+"\n            ")])}))],1),e._v(" "),a("md-whiteframe",{staticStyle:{width:"220px"}},[e.paramGroup?a("md-layout",{staticStyle:{padding:"30px 15px"},attrs:{"md-column":""}},[a("h2",{staticClass:"md-heading"},[e._v("\n              "+e._s(e.paramGroup.name)+"\n            ")]),e._v(" "),e._l(e.paramGroup.keys,function(t,r){return a("md-layout",{key:r,attrs:{"md-column":""}},["boolean"==e.params[t].type?a("div",[a("md-checkbox",{attrs:{type:"checkbox",tabindex:"0",id:t},model:{value:e.params[t].value,callback:function(a){e.$set(e.params[t],"value",a)},expression:"params[key].value"}},[e._v("\n                  "+e._s(e.params[t].label)+"\n                ")])],1):"drop_down"==e.params[t].type?a("div",[a("md-input-container",[a("label",[e._v(e._s(e.params[t].label))]),e._v(" "),a("md-select",{on:{change:function(a){e.selectDropDown(t)}},model:{value:e.params[t].value,callback:function(a){e.$set(e.params[t],"value",a)},expression:"params[key].value"}},e._l(e.params[t].options,function(t,r){return a("md-option",{key:r,attrs:{value:t}},[e._v("\n                      "+e._s(t)+"\n                    ")])}))],1)],1):"number"===e.params[t].type||"double"===e.params[t].type||"integer"===e.params[t].type?a("div",[a("md-input-container",[a("label",[e._v(e._s(e.params[t].label))]),e._v(" "),a("md-input",{attrs:{type:"number",step:"any"},model:{value:e.params[t].value,callback:function(a){e.$set(e.params[t],"value",a)},expression:"params[key].value"}})],1)],1):"slider"==e.params[t].type?a("div",[a("label",[e._v(e._s(e.params[t].label))]),e._v(" "),a("div",{staticStyle:{height:"2.5em"}}),e._v(" "),a("vue-slider",{attrs:{max:e.params[t].max,interval:e.params[t].interval},model:{value:e.params[t].value,callback:function(a){e.$set(e.params[t],"value",a)},expression:"params[key].value"}})],1):"breakpoints"==e.params[t].type?a("div",[a("label",[e._v(e._s(e.params[t].label))]),e._v(" "),a("div",{staticStyle:{height:"2.5em"}}),e._v(" "),e._l(e.params[t].value,function(r,s){return a("md-layout",{key:s,staticStyle:{width:"200px"},attrs:{"md-row":""}},[a("vue-slider",{staticStyle:{width:"130px"},attrs:{max:100,interval:1},on:{"drag-end":function(a){e.breakpointCallback(e.params,t)}},model:{value:e.params[t].value[s],callback:function(a){e.$set(e.params[t].value,s,a)},expression:"params[key].value[i]"}}),e._v(" "),a("md-button",{staticClass:"md-icon-button md-raised",on:{click:function(a){e.deleteBreakpoint(e.params,t,s)}}},[a("md-icon",[e._v("clear")])],1)],1)}),e._v(" "),a("md-button",{staticClass:"md-icon-button md-raised",on:{click:function(a){e.addBreakpoint(e.params,t)}}},[a("md-icon",[e._v("add")])],1)],2):e._e()])})],2):e._e()],1),e._v(" "),a("md-layout",{attrs:{"md-flex":""}},[a("div",{staticStyle:{width:"100%",padding:"30px 15px"}},[a("md-layout",{attrs:{"md-column":"","md-align":"start","md-vertical-align":"start"}},[a("h2",{staticClass:"md-heading"},[e._v("\n                Run model\n              ")]),e._v(" "),a("md-input-container",{staticStyle:{width:"200px"}},[a("label",[e._v("Existing Projects")]),e._v(" "),a("md-select",{on:{change:e.changeProject},model:{value:e.project,callback:function(t){e.project=t},expression:"project"}},e._l(e.projects,function(t,r){return a("md-option",{key:r,attrs:{value:t}},[e._v("\n                    "+e._s(t)+"\n                  ")])}))],1),e._v(" "),a("div",{staticStyle:{width:"100%"}},[a("md-layout",{attrs:{"md-row":"","md-vertical-align":"center"}},[a("md-button",{staticClass:"md-raised",attrs:{"md-flex":"true",disabled:e.isRunning},on:{click:function(t){e.run()}}},[e._v("\n                    Run\n                  ")]),e._v(" "),e.isRunning?a("md-spinner",{attrs:{"md-size":30,"md-indeterminate":""}}):e._e()],1)],1),e._v(" "),a("h2",{staticClass:"md-heading"},[e._v("\n                Console Output\n              ")]),e._v(" "),a("md-layout",{staticStyle:{width:"100%","background-color":"#EEE"}},[a("div",{staticStyle:{width:"100%",height:"350px","overflow-y":"scroll","font-family":"Courier, monospace","font-size":"0.9em"},attrs:{id:"console-output"}},e._l(e.consoleLines,function(t,r){return a("div",{key:r,staticStyle:{margin:"0 8px","word-wrap":"break-word"}},[e._v("\n                    "+e._s(t)+"\n                  ")])}))]),e._v(" "),a("h2",{directives:[{name:"show",rawName:"v-show",value:e.isGraph,expression:"isGraph"}],staticClass:"md-heading"},[e._v("\n                Progress in Uncertainty Runs\n              ")]),e._v(" "),a("md-layout",[a("div",{attrs:{id:"temp-chart-0"}}),e._v(" "),a("div",{attrs:{id:"temp-chart-1"}}),e._v(" "),a("div",{attrs:{id:"temp-chart-2"}}),e._v(" "),a("div",{attrs:{id:"temp-chart-3"}}),e._v(" "),a("div",{attrs:{id:"temp-chart-4"}}),e._v(" "),a("div",{attrs:{id:"temp-chart-5"}})]),e._v(" "),a("h2",{staticClass:"md-heading",staticStyle:{"margin-top":"1.5em"}},[e._v("\n                Model Results\n              ")]),e._v(" "),e.filenames.length>0?a("vue-slider",{staticStyle:{width:"100%"},attrs:{max:100,min:10,interval:1},on:{callback:function(t){e.changeWidth(e.imageWidth)}},model:{value:e.imageWidth,callback:function(t){e.imageWidth=t},expression:"imageWidth"}}):e._e(),e._v(" "),a("md-layout",{staticStyle:{width:"100%"}},e._l(e.filenames,function(t,r){return a("md-card",{key:r,style:e.imageStyle},[a("md-card-media",[a("img",{staticStyle:{width:"100%"},attrs:{src:t}})])],1)}))],1)],1)])],1)],1)],1)],1)},staticRenderFns:[]};var oe=a("VU/8")(se,ne,!1,function(e){a("oUpT")},"data-v-2a061b54",null).exports,ie={name:"Login",data:function(){return{title:d,email:"",rawPassword:"",error:""}},methods:{submit:function(){var e=this;return o()(s.a.mark(function t(){var a,r;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return a={email:e.$data.email,rawPassword:e.$data.rawPassword},console.log("> Login.submit",a),t.next=4,N.login(a);case 4:r=t.sent,console.log("> Login.submit response",r),r.result?e.$router.push("/"):e.error=r.error.message;case 7:case"end":return t.stop()}},t,e)}))()}}},le={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("md-layout",{attrs:{"md-align":"center"}},[a("md-whiteframe",{staticStyle:{"margin-top":"4em",padding:"3em"}},[a("md-layout",{attrs:{"md-flex":"50","md-align":"center","md-column":""}},[a("h2",{staticClass:"md-display-2"},[e._v("\n        Login to "+e._s(e.title)+"\n      ")]),e._v(" "),a("form",{staticClass:"login-screen",attrs:{novalidate:""},on:{submit:function(t){return t.preventDefault(),e.submit(t)}}},[a("md-input-container",[a("label",[e._v("E-mail address")]),e._v(" "),a("md-input",{attrs:{type:"text",placeholder:"E-mail address"},model:{value:e.email,callback:function(t){e.email=t},expression:"email"}})],1),e._v(" "),a("md-input-container",[a("label",[e._v("Password")]),e._v(" "),a("md-input",{attrs:{type:"password",placeholder:"Password"},model:{value:e.rawPassword,callback:function(t){e.rawPassword=t},expression:"rawPassword"}})],1),e._v(" "),a("md-button",{staticClass:"md-raised md-primary",attrs:{type:"submit"}},[e._v("login")]),e._v(" "),e.error?a("div",{staticStyle:{color:"red"}},[e._v("\n          "+e._s(e.error)+"\n        ")]):e._e(),e._v(" "),a("div",{staticStyle:{"margin-top":"3em"}},[e._v("\n          New to "+e._s(e.title)+"?  \n          "),a("router-link",{attrs:{to:"/register"}},[e._v("Register")])],1)],1)])],1)],1)},staticRenderFns:[]},ue=a("VU/8")(ie,le,!1,null,null,null).exports,ce={name:"Register",data:function(){return{title:d,name:"",email:"",rawPassword:"",rawPasswordConfirm:"",user:N.user,error:""}},methods:{submit:function(){var e=this;return o()(s.a.mark(function t(){var a,r;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return a={name:e.$data.name,email:e.$data.email,rawPassword:e.$data.rawPassword,rawPasswordConfirm:e.$data.rawPasswordConfirm},t.next=3,N.register(a);case 3:if(!(r=t.sent).result){t.next=9;break}return console.log("> Register.submit register success",r.result),t.next=8,N.login({email:a.email,rawPassword:a.rawPassword});case 8:r=t.sent;case 9:r.result?(console.log("> Register.submit login success",r.result),e.$router.push("/")):(console.log("> Register.submit fail",r.error),e.error=r.error.message);case 10:case"end":return t.stop()}},t,e)}))()}}},de={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("md-layout",{attrs:{"md-align":"center"}},[a("md-whiteframe",{staticStyle:{"margin-top":"4em",padding:"3em"}},[a("md-layout",{attrs:{"md-flex":"50","md-align":"center","md-column":""}},[a("h2",{staticClass:"md-display-2"},[e._v("\n        Register to "+e._s(e.title)+"\n      ")]),e._v(" "),a("form",{on:{submit:function(t){return t.preventDefault(),e.submit(t)}}},[a("md-input-container",[a("label",[e._v("User name")]),e._v(" "),a("md-input",{attrs:{type:"text",placeholder:"User name"},model:{value:e.name,callback:function(t){e.name=t},expression:"name"}})],1),e._v(" "),a("md-input-container",[a("label",[e._v("E-mail address")]),e._v(" "),a("md-input",{attrs:{type:"text",placeholder:"E-mail address"},model:{value:e.email,callback:function(t){e.email=t},expression:"email"}})],1),e._v(" "),a("md-input-container",[a("label",[e._v("Password")]),e._v(" "),a("md-input",{attrs:{type:"password",placeholder:"Password"},model:{value:e.rawPassword,callback:function(t){e.rawPassword=t},expression:"rawPassword"}})],1),e._v(" "),a("md-input-container",[a("label",[e._v("Confirm Password")]),e._v(" "),a("md-input",{attrs:{type:"password",placeholder:"Confirm Password"},model:{value:e.rawPasswordConfirm,callback:function(t){e.rawPasswordConfirm=t},expression:"rawPasswordConfirm"}})],1),e._v(" "),a("md-button",{staticClass:"md-raised md-primary",attrs:{type:"submit"}},[e._v("\n          Register\n        ")]),e._v(" "),e.error?a("div",{staticStyle:{color:"red"}},[e._v("\n          "+e._s(e.error)+"\n        ")]):e._e()],1)])],1)],1)},staticRenderFns:[]},pe=a("VU/8")(ce,de,!1,null,null,null).exports,me={name:"EditUser",data:function(){var e={};return f.a.assign(e,this.$store.state.user),f.a.assign(e,{title:"Edit Your Details",rawPassword:"",rawPasswordConfirm:"",error:""}),e},methods:{submit:function(){var e=this;return o()(s.a.mark(function t(){var a,r,n,o,i,l,u,c,d;return s.a.wrap(function(t){for(;;)switch(t.prev=t.next){case 0:for(e.error="",a={},r=["id","name","email","rawPassword","rawPasswordConfirm"],n=!0,o=!1,i=void 0,t.prev=6,l=j()(r);!(n=(u=l.next()).done);n=!0)c=u.value,e.$data[c]&&(a[c]=e.$data[c]);t.next=14;break;case 10:t.prev=10,t.t0=t.catch(6),o=!0,i=t.t0;case 14:t.prev=14,t.prev=15,!n&&l.return&&l.return();case 17:if(t.prev=17,!o){t.next=20;break}throw i;case 20:return t.finish(17);case 21:return t.finish(14);case 22:return t.next=24,N.update(a);case 24:(d=t.sent).result?e.error="User updated":(console.log("> EditUser.submit fail",d),e.error=d.error.message);case 26:case"end":return t.stop()}},t,e,[[6,10,14,22],[15,,17,21]])}))()}}},ve={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("md-layout",{attrs:{"md-align":"center"}},[a("md-whiteframe",{staticStyle:{"margin-top":"4em",padding:"3em"}},[a("md-layout",{attrs:{"md-flex":"50","md-align":"center","md-column":""}},[a("h2",{staticClass:"md-display-2"},[e._v("\n        "+e._s(e.title)+"\n      ")]),e._v(" "),a("form",{on:{submit:function(t){return t.preventDefault(),e.submit(t)}}},[a("md-input-container",[a("label",[e._v("User name")]),e._v(" "),a("md-input",{attrs:{type:"text",placeholder:"User name"},model:{value:e.name,callback:function(t){e.name=t},expression:"name"}})],1),e._v(" "),a("md-input-container",[a("label",[e._v("E-mail address")]),e._v(" "),a("md-input",{attrs:{type:"text",placeholder:"E-mail address"},model:{value:e.email,callback:function(t){e.email=t},expression:"email"}})],1),e._v(" "),a("md-input-container",[a("label",[e._v("New Password")]),e._v(" "),a("md-input",{attrs:{type:"password",placeholder:"New Password"},model:{value:e.rawPassword,callback:function(t){e.rawPassword=t},expression:"rawPassword"}})],1),e._v(" "),a("md-input-container",[a("label",[e._v("Confirm Password")]),e._v(" "),a("md-input",{attrs:{type:"password",placeholder:"Confirm Password"},model:{value:e.rawPasswordConfirm,callback:function(t){e.rawPasswordConfirm=t},expression:"rawPasswordConfirm"}})],1),e._v(" "),a("md-button",{staticClass:"md-raised md-primary",attrs:{type:"submit"}},[e._v("\n          Save\n        ")]),e._v(" "),e.error?a("div",{staticStyle:{color:"red"}},[e._v("\n          "+e._s(e.error)+"\n        ")]):e._e()],1)])],1)],1)},staticRenderFns:[]},he=a("VU/8")(me,ve,!1,null,null,null).exports;i.default.use(T.a);var fe,ge=new T.a({routes:[{path:"/",name:"model",component:oe},{path:"/login",name:"login",component:ue},{path:"/register",name:"register",component:pe},{path:"/edit-user",name:"editUser",component:he}]}),we=(fe=o()(s.a.mark(function e(){return s.a.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:if(!p){e.next=3;break}return e.next=3,N.restoreLastUser();case 3:return e.abrupt("return",new i.default({el:"#app",router:ge,store:L,template:"<App/>",components:{App:q}}));case 4:case"end":return e.stop()}},e,this)})),function(){return fe.apply(this,arguments)});i.default.config.productionTip=!1,i.default.use(u.a),i.default.material.registerTheme("default",{primary:"black"}),document.title=d,we()},oUpT:function(e,t){},rpYJ:function(e,t){},uslO:function(e,t,a){var r={"./af":"3CJN","./af.js":"3CJN","./ar":"3MVc","./ar-dz":"tkWw","./ar-dz.js":"tkWw","./ar-kw":"j8cJ","./ar-kw.js":"j8cJ","./ar-ly":"wPpW","./ar-ly.js":"wPpW","./ar-ma":"dURR","./ar-ma.js":"dURR","./ar-sa":"7OnE","./ar-sa.js":"7OnE","./ar-tn":"BEem","./ar-tn.js":"BEem","./ar.js":"3MVc","./az":"eHwN","./az.js":"eHwN","./be":"3hfc","./be.js":"3hfc","./bg":"lOED","./bg.js":"lOED","./bm":"hng5","./bm.js":"hng5","./bn":"aM0x","./bn.js":"aM0x","./bo":"w2Hs","./bo.js":"w2Hs","./br":"OSsP","./br.js":"OSsP","./bs":"aqvp","./bs.js":"aqvp","./ca":"wIgY","./ca.js":"wIgY","./cs":"ssxj","./cs.js":"ssxj","./cv":"N3vo","./cv.js":"N3vo","./cy":"ZFGz","./cy.js":"ZFGz","./da":"YBA/","./da.js":"YBA/","./de":"DOkx","./de-at":"8v14","./de-at.js":"8v14","./de-ch":"Frex","./de-ch.js":"Frex","./de.js":"DOkx","./dv":"rIuo","./dv.js":"rIuo","./el":"CFqe","./el.js":"CFqe","./en-au":"Sjoy","./en-au.js":"Sjoy","./en-ca":"Tqun","./en-ca.js":"Tqun","./en-gb":"hPuz","./en-gb.js":"hPuz","./en-ie":"ALEw","./en-ie.js":"ALEw","./en-il":"QZk1","./en-il.js":"QZk1","./en-nz":"dyB6","./en-nz.js":"dyB6","./eo":"Nd3h","./eo.js":"Nd3h","./es":"LT9G","./es-do":"7MHZ","./es-do.js":"7MHZ","./es-us":"INcR","./es-us.js":"INcR","./es.js":"LT9G","./et":"XlWM","./et.js":"XlWM","./eu":"sqLM","./eu.js":"sqLM","./fa":"2pmY","./fa.js":"2pmY","./fi":"nS2h","./fi.js":"nS2h","./fo":"OVPi","./fo.js":"OVPi","./fr":"tzHd","./fr-ca":"bXQP","./fr-ca.js":"bXQP","./fr-ch":"VK9h","./fr-ch.js":"VK9h","./fr.js":"tzHd","./fy":"g7KF","./fy.js":"g7KF","./gd":"nLOz","./gd.js":"nLOz","./gl":"FuaP","./gl.js":"FuaP","./gom-latn":"+27R","./gom-latn.js":"+27R","./gu":"rtsW","./gu.js":"rtsW","./he":"Nzt2","./he.js":"Nzt2","./hi":"ETHv","./hi.js":"ETHv","./hr":"V4qH","./hr.js":"V4qH","./hu":"xne+","./hu.js":"xne+","./hy-am":"GrS7","./hy-am.js":"GrS7","./id":"yRTJ","./id.js":"yRTJ","./is":"upln","./is.js":"upln","./it":"FKXc","./it.js":"FKXc","./ja":"ORgI","./ja.js":"ORgI","./jv":"JwiF","./jv.js":"JwiF","./ka":"RnJI","./ka.js":"RnJI","./kk":"j+vx","./kk.js":"j+vx","./km":"5j66","./km.js":"5j66","./kn":"gEQe","./kn.js":"gEQe","./ko":"eBB/","./ko.js":"eBB/","./ky":"6cf8","./ky.js":"6cf8","./lb":"z3hR","./lb.js":"z3hR","./lo":"nE8X","./lo.js":"nE8X","./lt":"/6P1","./lt.js":"/6P1","./lv":"jxEH","./lv.js":"jxEH","./me":"svD2","./me.js":"svD2","./mi":"gEU3","./mi.js":"gEU3","./mk":"Ab7C","./mk.js":"Ab7C","./ml":"oo1B","./ml.js":"oo1B","./mr":"5vPg","./mr.js":"5vPg","./ms":"ooba","./ms-my":"G++c","./ms-my.js":"G++c","./ms.js":"ooba","./mt":"oCzW","./mt.js":"oCzW","./my":"F+2e","./my.js":"F+2e","./nb":"FlzV","./nb.js":"FlzV","./ne":"/mhn","./ne.js":"/mhn","./nl":"3K28","./nl-be":"Bp2f","./nl-be.js":"Bp2f","./nl.js":"3K28","./nn":"C7av","./nn.js":"C7av","./pa-in":"pfs9","./pa-in.js":"pfs9","./pl":"7LV+","./pl.js":"7LV+","./pt":"ZoSI","./pt-br":"AoDM","./pt-br.js":"AoDM","./pt.js":"ZoSI","./ro":"wT5f","./ro.js":"wT5f","./ru":"ulq9","./ru.js":"ulq9","./sd":"fW1y","./sd.js":"fW1y","./se":"5Omq","./se.js":"5Omq","./si":"Lgqo","./si.js":"Lgqo","./sk":"OUMt","./sk.js":"OUMt","./sl":"2s1U","./sl.js":"2s1U","./sq":"V0td","./sq.js":"V0td","./sr":"f4W3","./sr-cyrl":"c1x4","./sr-cyrl.js":"c1x4","./sr.js":"f4W3","./ss":"7Q8x","./ss.js":"7Q8x","./sv":"Fpqq","./sv.js":"Fpqq","./sw":"DSXN","./sw.js":"DSXN","./ta":"+7/x","./ta.js":"+7/x","./te":"Nlnz","./te.js":"Nlnz","./tet":"gUgh","./tet.js":"gUgh","./tg":"5SNd","./tg.js":"5SNd","./th":"XzD+","./th.js":"XzD+","./tl-ph":"3LKG","./tl-ph.js":"3LKG","./tlh":"m7yE","./tlh.js":"m7yE","./tr":"k+5o","./tr.js":"k+5o","./tzl":"iNtv","./tzl.js":"iNtv","./tzm":"FRPF","./tzm-latn":"krPU","./tzm-latn.js":"krPU","./tzm.js":"FRPF","./ug-cn":"To0v","./ug-cn.js":"To0v","./uk":"ntHu","./uk.js":"ntHu","./ur":"uSe8","./ur.js":"uSe8","./uz":"XU1s","./uz-latn":"/bsm","./uz-latn.js":"/bsm","./uz.js":"XU1s","./vi":"0X8Q","./vi.js":"0X8Q","./x-pseudo":"e/KL","./x-pseudo.js":"e/KL","./yo":"YXlc","./yo.js":"YXlc","./zh-cn":"Vz2w","./zh-cn.js":"Vz2w","./zh-hk":"ZUyn","./zh-hk.js":"ZUyn","./zh-tw":"BbgG","./zh-tw.js":"BbgG"};function s(e){return a(n(e))}function n(e){var t=r[e];if(!(t+1))throw new Error("Cannot find module '"+e+"'.");return t}s.keys=function(){return Object.keys(r)},s.resolve=n,e.exports=s,s.id="uslO"}},["NHnr"]);
//# sourceMappingURL=app.29c4ab4afa2e383abdd0.js.map