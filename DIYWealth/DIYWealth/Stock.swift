//
//  Stock.swift
//  DIYWealth
//
//  Created by John Walker on 23/01/2019.
//  Copyright © 2019 DIYWealth. All rights reserved.
//

import UIKit

class Stock: NSObject {
    
    var symbol: String
    var name: String
    var rank: Int
    var pe: Double
    var roe: Double
    var marketcap: Double

    init?(symbol: String, name: String, rank: Int, pe: Double, roe: Double, marketcap: Double) {
        
        // Initialisation should fail if the inputs are not correct.
        
        // The symbol and name must not be empty
        guard !symbol.isEmpty && !name.isEmpty else {
            return nil
        }
        
        // The rating must be between 0 and 5 inclusively
        guard (rank > 0) && (pe > 0.0) && (roe > 0.0) && (marketcap > 0.0) else {
            return nil
        }
        
        // Initialize stored properties.
        self.symbol = symbol
        self.name = name
        self.rank = rank
        self.pe = pe
        self.roe = roe
        self.marketcap = marketcap
        
    }

}
