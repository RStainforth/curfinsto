//
//  PortfolioViewController.swift
//  DIYWealth
//
//  Created by John Walker on 20/01/2019.
//  Copyright © 2019 DIYWealth. All rights reserved.
//

import UIKit
import Charts // You need this line to be able to use Charts Library

class PortfolioViewController: UIViewController {

    @IBOutlet weak var chartView: LineChartView!
    
    // Store the data in example array for now
    // In the future this will come from the database
    let portfolio : [Double] = [0.0, 0.3, 0.5, 0.4, 0.7, 0.9, 0.8, 1.1, 1.3, 1.4, 1.4, 1.6]
    let index : [Double]     = [0.0, 0.2, 0.4, 0.5, 0.4, 0.6, 0.9, 0.7, 0.9, 1.1, 1.3, 1.3]
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        plotGraph()
    }
    
    func plotGraph() {
    
        var portfolioLineChartEntry  = [ChartDataEntry]() //this is the Array that will eventually be displayed on the graph.
        var indexLineChartEntry  = [ChartDataEntry]() //this is the Array that will eventually be displayed on the graph.
        
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd HH:mm"
        //var dateTime = dateFormatter.date(from: "2019/01/01 00:00")!.timeIntervalSince1970
        var dateTime = dateFormatter.date(from: "2019/01/01 00:00")
        //let daySeconds: TimeInterval = 86400
    
        //here is the for loop
        for i in 0..<portfolio.count {
            
            let intervalDate = dateTime!.timeIntervalSince1970
    
            let portfolioValue = ChartDataEntry(x: intervalDate, y: portfolio[i]) // here we set the X and Y status in a data chart entry
            let indexValue = ChartDataEntry(x: intervalDate, y: index[i]) // here we set the X and Y status in a data chart entry
            
            //dateTime = dateTime + (Double(i)*daySeconds)
            dateTime = Calendar.current.date(byAdding: .day, value: 1, to: dateTime!)

            portfolioLineChartEntry.append(portfolioValue) // here we add it to the data set
            indexLineChartEntry.append(indexValue) // here we add it to the data set
    
        }
    
        let portfolioLine = LineChartDataSet(values: portfolioLineChartEntry, label: "Portfolio") //Here we convert lineChartEntry to a LineChartDataSet
        let indexLine = LineChartDataSet(values: indexLineChartEntry, label: "Index") //Here we convert lineChartEntry to a LineChartDataSet
    
        portfolioLine.colors = [UIColor(red:0.25, green:0.06, blue:0.25, alpha:1.0)] //Sets the colour to purple
        indexLine.colors = [UIColor(red:0.95, green:0.56, blue:0.01, alpha:1.0)] //Sets the colour to orange
        
        portfolioLine.axisDependency = .left
        //portfolioLine.setColor(UIColor(red: 51/255, green: 181/255, blue: 229/255, alpha: 1))
        portfolioLine.lineWidth = 4.0
        portfolioLine.drawCirclesEnabled = false
        portfolioLine.drawValuesEnabled = false
        //portfolioLine.fillAlpha = 0.26
        //portfolioLine.fillColor = UIColor(red: 51/255, green: 181/255, blue: 229/255, alpha: 1)
        //portfolioLine.highlightColor = UIColor(red: 244/255, green: 117/255, blue: 117/255, alpha: 1)
        portfolioLine.drawCircleHoleEnabled = false
        
        indexLine.axisDependency = .left
        //indexLine.setColor(UIColor(red: 51/255, green: 181/255, blue: 229/255, alpha: 1))
        indexLine.lineWidth = 4.0
        indexLine.drawCirclesEnabled = false
        indexLine.drawValuesEnabled = false
        //indexLine.fillAlpha = 0.26
        //indexLine.fillColor = UIColor(red: 51/255, green: 181/255, blue: 229/255, alpha: 1)
        //indexLine.highlightColor = UIColor(red: 244/255, green: 117/255, blue: 117/255, alpha: 1)
        indexLine.drawCircleHoleEnabled = false
    
        let data = LineChartData() //This is the object that will be added to the chart
    
        data.addDataSet(portfolioLine) //Adds the line to the dataSet
        data.addDataSet(indexLine) //Adds the line to the dataSet
    
        chartView.data = data //finally - it adds the chart data to the chart and causes an update
    
        chartView.chartDescription?.text = "Portfolio vs Index" // Here we set the description for the graph
        
        //chartView.chartDescription?.enabled = false
        
        //chartView.dragEnabled = true
        //chartView.setScaleEnabled(true)
        //chartView.pinchZoomEnabled = false
        //chartView.highlightPerDragEnabled = true
        
        //chartView.backgroundColor = .white
        
        //chartView.legend.enabled = false
        
        let xAxis = chartView.xAxis
        //xAxis.labelPosition = .topInside
        //xAxis.labelFont = .systemFont(ofSize: 10, weight: .light)
        //xAxis.labelTextColor = UIColor(red: 255/255, green: 192/255, blue: 56/255, alpha: 1)
        //xAxis.drawAxisLineEnabled = false
        //xAxis.drawGridLinesEnabled = true
        //xAxis.centerAxisLabelsEnabled = true
        xAxis.granularity = 3600
        xAxis.valueFormatter = DateValueFormatter()
        
        //let leftAxis = chartView.leftAxis
        //leftAxis.labelPosition = .insideChart
        //leftAxis.labelFont = .systemFont(ofSize: 12, weight: .light)
        //leftAxis.drawGridLinesEnabled = true
        //leftAxis.granularityEnabled = true
        //leftAxis.axisMinimum = 0
        //leftAxis.axisMaximum = 170
        //leftAxis.yOffset = -9
        //leftAxis.labelTextColor = UIColor(red: 255/255, green: 192/255, blue: 56/255, alpha: 1)
        
        
        chartView.rightAxis.enabled = false
        
        //chartView.legend.form = .line
        
        chartView.animate(xAxisDuration: 2.5)

    }
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
