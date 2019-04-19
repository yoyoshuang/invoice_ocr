#coding:utf-8
import numpy as np
# //************************************
# // 函数名称: sauvola
# // 函数说明: 局部均值二值化
# // 参    数:
# //           const unsigned char * grayImage        [in]        输入图像数据
# //           const unsigned char * biImage          [out]       输出图像数据     
# //           const int w                            [in]        输入输出图像数据宽
# //           const int h                            [in]        输入输出图像数据高
# //           const int k                            [in]        threshold = mean*(1 + k*((std / 128) - 1))
# //           const int windowSize                   [in]        处理区域宽高
# // 返 回 值: void
# //************************************
def sauvola(grayImage,  k,  windowSize):

    whalf = windowSize/2;
    IMAGE_WIDTH= grayImage.shape[1];
    IMAGE_HEIGHT = grayImage.shape[0];
    # create the integral image
    integralImg = np.zeros(grayImage.shape)
    integralImgSqrt = np.zeros(grayImage.shape)
    biImage = np.zeros(grayImage.shape)#coding:utf-8
    pixsum = 0;
    sqrtsum = 0;
    # print grayImage.shape
    #收集数据 integralImg像素和积分图 integralImgSqrt像素平方和积分图
    for i in range(IMAGE_HEIGHT):
        # reset this column sum
        pixsum = 0;
        sqrtsum = 0;
        for  j in range(IMAGE_WIDTH):        
            # index = i*IMAGE_WIDTH + j
            # print (i,j)
            pixsum += grayImage[i,j]
            sqrtsum += grayImage[i,j] * grayImage[i,j]
            if i == 0:

                integralImg[i,j] = pixsum
                integralImgSqrt[i,j] = sqrtsum
            else:
                integralImgSqrt[i,j] = integralImgSqrt[(i - 1),j] + sqrtsum
                integralImg[i,j] = integralImg[(i - 1),j] + pixsum
        

    #Calculate the mean and standard deviation using the integral image
    # int xmin, ymin, xmax, ymax;
    # double mean, std, threshold;
    # double diagsum, idiagsum, diff, sqdiagsum, sqidiagsum, sqdiff, area;
    for i in range(IMAGE_HEIGHT):
        for j in range(IMAGE_WIDTH): 
            xmin = max(0, i - whalf)
            ymin = max(0, j - whalf)
            xmax = min(IMAGE_HEIGHT - 1, i + whalf)
            ymax = min(IMAGE_WIDTH - 1, j + whalf)
            area = (xmax - xmin + 1) * (ymax - ymin + 1)
            if area <= 0:
                biImage[i ,j] = 255
                continue
            
            if (xmin == 0 and ymin == 0):
                diff = integralImg[xmax,ymax]
                sqdiff = integralImgSqrt[xmax,ymax]
            
            elif (xmin > 0 and ymin == 0):
                diff = integralImg[xmax,ymax] - integralImg[xmin - 1,ymax]
                sqdiff = integralImgSqrt[xmax,ymax] - integralImgSqrt[xmin - 1,ymax]
            
            elif (xmin == 0 and ymin > 0):
                diff = integralImg[xmax,ymax] - integralImg[xmax,(ymin - 1)]
                sqdiff = integralImgSqrt[xmax,ymax] - integralImgSqrt[xmax,(ymin - 1)]
            
            else:
                diagsum = integralImg[xmax,ymax] + integralImg[xmin - 1,(ymin - 1) ]
                idiagsum = integralImg[xmax,(ymin - 1)] + integralImg[xmin - 1,ymax]
                diff = diagsum - idiagsum;
                sqdiagsum = integralImgSqrt[xmax,ymax] + integralImgSqrt[xmin - 1,(ymin - 1)]
                sqidiagsum = integralImgSqrt[xmax,(ymin - 1)] + integralImgSqrt[xmin - 1,ymax]
                sqdiff = sqdiagsum - sqidiagsum
            
            mean = diff / area
            std = np.sqrt((sqdiff - diff*diff / area) / (area - 1))
            threshold = mean*(1 + k*((std / 128) - 1))
            if (grayImage[i,j] > threshold):
                biImage[i,j] = 0
            else:
                biImage[i,j] = 1
        
    
    return biImage

