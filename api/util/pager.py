# coding: utf-8
#智能分页类
import math

class pager:
	
	surfix=""
	
	def __init__(self,link_str,per_page=20,now_page=1):
		self.link_str="<li><a href=\"%s" % link_str
		self.per_page=per_page
		self.now_page=now_page
		self.from_num=0
		self.end_num=0


	def set_surfix(self,surfix):
		self.surfix=surfix


	def get_now_page(self):
		return self.now_page

	def set_now_page(self,now_page):
		self.now_page = now_page
		self.set_from_num((self.get_now_page()-1)*self.get_per_page())

	
	def get_per_page(self):
		return self.per_page

	def set_per_page(self,per_page):
		self.per_page = per_page

	def get_total_page(self):
		return self.total_page

	def set_total_page(self,total_page):
		self.total_page =1 if (total_page<=0) else total_page

	def get_total_result(self):
		return self.total_result

	def set_total_result(self,total_result):
		self.total_result = total_result
		#自动设定total_page
		self.set_total_page(  math.floor((self.total_result-1)/self.per_page)+1)
		self.set_from_num((self.get_now_page()-1)*self.get_per_page())
		end_num=self.get_total_result() if (self.get_now_page()*self.get_per_page()>self.get_total_result()) else  self.get_now_page()*self.get_per_page()
		self.set_end_num(end_num)

	
	def set_end_num(self,end_num):
		self.end_num = end_num


	def set_from_num(self,from_num):
		self.from_num = from_num

	def get_from_num(self):
		return self.from_num

	
	def get_end_num(self):
		return self.end_num


	#实现分页
	def get_page_nav(self,current_page,iPart=7):

		nav=""	
		fir=(current_page-1) if (current_page-1)>0 else 1
		
		fina=self.get_total_page() if ((current_page+1)>self.get_total_page()) else (current_page+1)
		nav="%s%d%s\">Prev</a></li> \n" % (self.link_str,fir,self.surfix)

		temp=int(current_page+1)
		cend=int(self.total_page if (temp+iPart)>=self.total_page else (temp+iPart)) 

		cover=(current_page-iPart+1) if (current_page-iPart)>=0 else 1

	  	for b in xrange(cover,current_page+1):
			if b==current_page:
				nav+="<li class=\"active\"><a href='#'>%d</a></li>\n" % b
			else: 
				nav+="%s%d%s\">%d</a></li> \n" % (self.link_str,b,self.surfix,b)
	
		for m in xrange(temp,cend+1):
			nav+=("%s%d%s\">%d</a> </li> " % (self.link_str,m,self.surfix,m))
		nav+=("%s%d%s\">Next</a></li> " % (self.link_str,fina,self.surfix))

		return nav

	'''
	大跨度分页.
	Page Division
	
	def get_page_division():
		div=""
		dstep=500
		maxpovit=math.ceil(self.total_page/( dstep))
		for i in xrange(maxpovit):
			if(self.now_page<(i+1)*dstep && self.now_page>=(i*dstep)): 
				div.=((preg_replace("/<li>(.*?)/i", "<li class=\"active\">1", self.link_str).(i*dstep==0?1:i*dstep)).self.surfix."\">".(i*dstep==0?1:i*dstep)."-".(i*dstep+dstep)."</a></li>") }
			else:
				div+=(self.link_str.(i*dstep==0?1:i*dstep).self.surfix."\">".(i*dstep==0?1:i*dstep)."-".(i*dstep+dstep)."</a></li>")
		return div
	'''
	def get_link_str(self):
		return self.link_str
