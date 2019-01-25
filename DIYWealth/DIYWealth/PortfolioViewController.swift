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

    @IBOutlet weak var chtChart: LineChartView!
    
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
    
        //here is the for loop
        for i in 0..<portfolio.count {
    
            let portfolioValue = ChartDataEntry(x: Double(i), y: portfolio[i]) // here we set the X and Y status in a data chart entry
            let indexValue = ChartDataEntry(x: Double(i), y: index[i]) // here we set the X and Y status in a data chart entry

            portfolioLineChartEntry.append(portfolioValue) // here we add it to the data set
            indexLineChartEntry.append(indexValue) // here we add it to the data set
    
        }
    
        let portfolioLine = LineChartDataSet(values: portfolioLineChartEntry, label: "Portfolio") //Here we convert lineChartEntry to a LineChartDataSet
        let indexLine = LineChartDataSet(values: indexLineChartEntry, label: "Index") //Here we convert lineChartEntry to a LineChartDataSet
    
        portfolioLine.colors = [NSUIColor.blue] //Sets the colour to blue
        indexLine.colors = [NSUIColor.red] //Sets the colour to blue
    
        let data = LineChartData() //This is the object that will be added to the chart
    
        data.addDataSet(portfolioLine) //Adds the line to the dataSet
        data.addDataSet(indexLine) //Adds the line to the dataSet
    
        chtChart.data = data //finally - it adds the chart data to the chart and causes an update
    
        chtChart.chartDescription?.text = "Portfolio vs Index" // Here we set the description for the graph

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
